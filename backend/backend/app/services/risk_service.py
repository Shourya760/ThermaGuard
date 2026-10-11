"""
app/services/risk_service.py

Deterministic heat-risk engine.
Calculates a 0-100 risk score based on available weather and zone heat indicators.

Assumptions and Methodology (Version 1.0):
- Relies on current air temperature/apparent temperature as a baseline.
- Satellite Land Surface Temperature (LST), Vegetation, Shade, and Vulnerability are intended 
  modifiers.
- If ANY of these key modifiers are missing, the score is explicitly NOT calculated. 
  It returns 'insufficient_data'.
- Air temperature alone is NOT treated as a neighborhood risk score, as it doesn't account 
  for the urban heat island effect or local vulnerability.
- Not a validated medical index.
"""

from typing import Dict, Any

from app.schemas.zone import ZoneDetail
from app.schemas.weather import WeatherResponse
from app.schemas.risk import RiskResponse


class RiskService:
    """
    Deterministic heat-risk calculation service.
    """
    
    VERSION = "1.0"
    METHODOLOGY = (
        "Deterministic model calculating a 0-100 risk score based on the equation: "
        "Score = (BaseTemp + LST_Modifier + Veg_Modifier + Shade_Modifier) * Vuln_Multiplier.\n"
        "- BaseTemp: Normalizes air temp from 25C to 45C -> 0 to 100.\n"
        "- LST_Modifier: (LST - AirTemp) * 2, capped between -10 and +20.\n"
        "- Veg_Modifier: -15 * (Vegetation % / 100).\n"
        "- Shade_Modifier: -10 * (Shade % / 100).\n"
        "- Vuln_Multiplier: 0.8 + (Vulnerability Index * 0.5) -> range 0.8 to 1.3.\n"
        "If any required indicator is missing, calculation is aborted."
    )
    LIMITATIONS = [
        "This is NOT a validated medical or public-health heat-risk index.",
        "Air temperature is taken from a regional weather model, not micro-local sensors.",
        "LST, vegetation, and shade data rely on periodic satellite passes, not real-time.",
    ]

    # Required indicators for a valid score
    REQUIRED_INDICATORS = [
        "temperature_celsius",
        "land_surface_temperature_celsius",
        "vegetation_coverage_percent",
        "shade_coverage_percent",
        "population_vulnerability_index"
    ]

    def calculate_risk(self, zone: ZoneDetail, weather: WeatherResponse) -> RiskResponse:
        """
        Evaluate risk for a zone based on weather and static indicators.
        """
        inputs: Dict[str, Any] = {}
        missing: list[str] = []
        
        # Gather weather inputs
        if weather.temperature_celsius is not None:
            inputs["temperature_celsius"] = weather.temperature_celsius
        else:
            missing.append("temperature_celsius")
            
        if weather.apparent_temperature_celsius is not None:
            inputs["apparent_temperature_celsius"] = weather.apparent_temperature_celsius
            
        if weather.relative_humidity_percent is not None:
            inputs["relative_humidity_percent"] = weather.relative_humidity_percent

        # Gather zone inputs
        hi = zone.heat_indicators
        if hi.land_surface_temperature_celsius is not None:
            inputs["land_surface_temperature_celsius"] = hi.land_surface_temperature_celsius
        else:
            missing.append("land_surface_temperature_celsius")
            
        if hi.vegetation_coverage_percent is not None:
            inputs["vegetation_coverage_percent"] = hi.vegetation_coverage_percent
        else:
            missing.append("vegetation_coverage_percent")
            
        if hi.shade_coverage_percent is not None:
            inputs["shade_coverage_percent"] = hi.shade_coverage_percent
        else:
            missing.append("shade_coverage_percent")
            
        if hi.population_vulnerability_index is not None:
            inputs["population_vulnerability_index"] = hi.population_vulnerability_index
        else:
            missing.append("population_vulnerability_index")

        # Check if we have sufficient data
        if missing:
            return RiskResponse(
                zone_id=zone.id,
                status="insufficient_data",
                score=None,
                category=None,
                methodology_version=self.VERSION,
                methodology_description=self.METHODOLOGY,
                limitations=self.LIMITATIONS,
                inputs_used=inputs,
                missing_indicators=missing,
                contributing_factors=None
            )
            
        # Validate values to reject unrealistic data
        invalid_reasons = []
        if not (-50 <= inputs["temperature_celsius"] <= 60):
            invalid_reasons.append("Air temperature must be between -50C and +60C.")
        if not (-50 <= inputs["land_surface_temperature_celsius"] <= 80):
            invalid_reasons.append("LST must be between -50C and +80C.")
        if not (0 <= inputs["vegetation_coverage_percent"] <= 100):
            invalid_reasons.append("Vegetation coverage must be 0-100%.")
        if not (0 <= inputs["shade_coverage_percent"] <= 100):
            invalid_reasons.append("Shade coverage must be 0-100%.")
        if not (0 <= inputs["population_vulnerability_index"] <= 1):
            invalid_reasons.append("Vulnerability index must be 0-1.")
            
        if invalid_reasons:
            raise ValueError("Invalid indicator values: " + " ".join(invalid_reasons))
            
        # --- Scoring Logic (Deterministic) ---
        # If we reach here, we have all required inputs. 
        # (Note: In Phase 4/5 demo data, this will never be reached because hi.* are null,
        # but the logic must exist and be tested).
        
        # 1. Base temp score (Normalize 25C to 45C -> 0 to 100)
        temp = inputs["temperature_celsius"]
        base_score = max(0, min(100, (temp - 25) * 5))
        
        # 2. LST modifier (Adds or subtracts up to 20 points depending on how much LST exceeds air temp)
        lst = inputs["land_surface_temperature_celsius"]
        lst_diff = lst - temp
        lst_modifier = max(-10, min(20, lst_diff * 2))
        
        # 3. Vegetation cooling modifier (Reduces score by up to 15 points)
        veg = inputs["vegetation_coverage_percent"]
        veg_modifier = -15 * (veg / 100.0)
        
        # 4. Shade cooling modifier (Reduces score by up to 10 points)
        shade = inputs["shade_coverage_percent"]
        shade_modifier = -10 * (shade / 100.0)
        
        # 5. Vulnerability multiplier (Scales the final score 0.8x to 1.3x)
        vuln = inputs["population_vulnerability_index"]
        vuln_multiplier = 0.8 + (vuln * 0.5)  # 0 -> 0.8, 1 -> 1.3
        
        # Aggregate
        raw_score = (base_score + lst_modifier + veg_modifier + shade_modifier) * vuln_multiplier
        final_score = round(max(0, min(100, raw_score)), 1)
        
        # Categorize
        if final_score < 30:
            category = "Low"
        elif final_score < 60:
            category = "Moderate"
        elif final_score < 80:
            category = "High"
        else:
            category = "Extreme"
            
        factors = {
            "base_temperature_score": round(base_score, 1),
            "lst_modifier": round(lst_modifier, 1),
            "vegetation_modifier": round(veg_modifier, 1),
            "shade_modifier": round(shade_modifier, 1),
            "vulnerability_multiplier": round(vuln_multiplier, 2)
        }

        return RiskResponse(
            zone_id=zone.id,
            status="score_available",
            score=final_score,
            category=category,
            methodology_version=self.VERSION,
            methodology_description=self.METHODOLOGY,
            limitations=self.LIMITATIONS,
            inputs_used=inputs,
            missing_indicators=[],
            contributing_factors=factors
        )

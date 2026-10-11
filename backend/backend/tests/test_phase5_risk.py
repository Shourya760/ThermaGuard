"""
tests/test_phase5_risk.py

Tests for Phase 5 - Explainable Heat-Risk Engine.
Tests all-null inputs, partially missing inputs, valid complete inputs, 
boundary conditions, deterministic outputs, and unknown zone IDs.
Uses mocked WeatherService responses so no internet is required.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.risk_service import RiskService
from app.schemas.zone import ZoneDetail, HeatIndicators
from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherServiceError

client = TestClient(app)

KNOWN_ZONE = "delhi-connaught-place"


# --- Service tests ---

class TestRiskService:
    service = RiskService()
    
    def test_insufficient_data_when_indicators_null(self):
        zone = ZoneDetail(
            id="test-zone",
            name="Test",
            city="City",
            country="Country",
            latitude=0.0,
            longitude=0.0,
            area_type="residential",
            description="",
            coordinate_source="",
            data_provenance="",
            data_status="DEMO",
            heat_indicators=HeatIndicators() # all null
        )
        weather = WeatherResponse(
            source="test",
            latitude=0.0,
            longitude=0.0,
            temperature_celsius=35.0
        )
        
        result = self.service.calculate_risk(zone, weather)
        assert result.status == "insufficient_data"
        assert result.score is None
        assert "land_surface_temperature_celsius" in result.missing_indicators
        assert "vegetation_coverage_percent" in result.missing_indicators
        assert "shade_coverage_percent" in result.missing_indicators
        assert "population_vulnerability_index" in result.missing_indicators
        
    def test_insufficient_data_when_weather_temp_null(self):
        zone = ZoneDetail(
            id="test-zone",
            name="Test",
            city="City",
            country="Country",
            latitude=0.0,
            longitude=0.0,
            area_type="residential",
            description="",
            coordinate_source="",
            data_provenance="",
            data_status="VERIFIED",
            heat_indicators=HeatIndicators(
                land_surface_temperature_celsius=40.0,
                vegetation_coverage_percent=10.0,
                shade_coverage_percent=5.0,
                population_vulnerability_index=0.5
            )
        )
        weather = WeatherResponse(
            source="test",
            latitude=0.0,
            longitude=0.0,
            temperature_celsius=None # missing temp
        )
        
        result = self.service.calculate_risk(zone, weather)
        assert result.status == "insufficient_data"
        assert result.score is None
        assert "temperature_celsius" in result.missing_indicators
        
    def test_valid_complete_inputs_calculate_deterministic_score(self):
        zone = ZoneDetail(
            id="test-zone",
            name="Test",
            city="City",
            country="Country",
            latitude=0.0,
            longitude=0.0,
            area_type="residential",
            description="",
            coordinate_source="",
            data_provenance="",
            data_status="VERIFIED",
            heat_indicators=HeatIndicators(
                land_surface_temperature_celsius=40.0,
                vegetation_coverage_percent=20.0,
                shade_coverage_percent=10.0,
                population_vulnerability_index=0.8
            )
        )
        weather = WeatherResponse(
            source="test",
            latitude=0.0,
            longitude=0.0,
            temperature_celsius=35.0
        )
        
        # Calculation breakdown:
        # Base: (35-25)*5 = 50
        # LST mod: (40-35)*2 = 10
        # Veg mod: -15 * 0.2 = -3
        # Shade mod: -10 * 0.1 = -1
        # Vuln mult: 0.8 + 0.8*0.5 = 1.2
        # Score: (50 + 10 - 3 - 1) * 1.2 = 56 * 1.2 = 67.2
        
        result = self.service.calculate_risk(zone, weather)
        assert result.status == "score_available"
        assert result.score == 67.2
        assert result.category == "High"
        assert not result.missing_indicators
        
    def test_invalid_values_raise_value_error(self):
        zone = ZoneDetail(
            id="test-zone", name="Test", city="C", country="C", latitude=0.0, longitude=0.0, area_type="res", description="", coordinate_source="", data_provenance="", data_status="VERIFIED",
            heat_indicators=HeatIndicators(
                land_surface_temperature_celsius=40.0,
                vegetation_coverage_percent=150.0, # INVALID
                shade_coverage_percent=10.0,
                population_vulnerability_index=0.8
            )
        )
        weather = WeatherResponse(
            source="test", latitude=0.0, longitude=0.0, temperature_celsius=35.0
        )
        with pytest.raises(ValueError, match="Vegetation coverage"):
            self.service.calculate_risk(zone, weather)
        
    def test_score_boundaries(self):
        # Extreme heat, high vuln
        zone = ZoneDetail(
            id="test-zone",
            name="Test", city="C", country="C", latitude=0.0, longitude=0.0, area_type="res", description="", coordinate_source="", data_provenance="", data_status="VERIFIED",
            heat_indicators=HeatIndicators(land_surface_temperature_celsius=55.0, vegetation_coverage_percent=0.0, shade_coverage_percent=0.0, population_vulnerability_index=1.0)
        )
        weather = WeatherResponse(source="test", latitude=0.0, longitude=0.0, temperature_celsius=50.0)
        result = self.service.calculate_risk(zone, weather)
        assert result.score == 100.0 # capped
        
        # Cold, low vuln
        zone2 = ZoneDetail(
            id="test-zone2",
            name="Test", city="C", country="C", latitude=0.0, longitude=0.0, area_type="res", description="", coordinate_source="", data_provenance="", data_status="VERIFIED",
            heat_indicators=HeatIndicators(land_surface_temperature_celsius=10.0, vegetation_coverage_percent=100.0, shade_coverage_percent=100.0, population_vulnerability_index=0.0)
        )
        weather2 = WeatherResponse(source="test", latitude=0.0, longitude=0.0, temperature_celsius=15.0)
        result2 = self.service.calculate_risk(zone2, weather2)
        assert result2.score == 0.0 # floored


# --- Endpoint tests ---

class TestRiskEndpoint:

    @patch("app.routes.risk._weather_service.get_current_weather")
    def test_get_risk_insufficient_data(self, mock_weather):
        mock_weather.return_value = WeatherResponse(
            source="test", latitude=28.6, longitude=77.2, temperature_celsius=38.4
        )
        
        response = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "insufficient_data"
        assert data["score"] is None
        assert "land_surface_temperature_celsius" in data["missing_indicators"]
        
    @patch("app.routes.risk._weather_service.get_current_weather")
    @patch("app.routes.risk._zone_service.get_zone")
    def test_get_risk_score_available(self, mock_get_zone, mock_weather):
        zone_mock = ZoneDetail(
            id=KNOWN_ZONE, name="Test", city="C", country="C", latitude=0.0, longitude=0.0, area_type="res", description="", coordinate_source="", data_provenance="", data_status="VERIFIED",
            heat_indicators=HeatIndicators(land_surface_temperature_celsius=40.0, vegetation_coverage_percent=20.0, shade_coverage_percent=10.0, population_vulnerability_index=0.5)
        )
        mock_get_zone.return_value = zone_mock
        mock_weather.return_value = WeatherResponse(
            source="test", latitude=0.0, longitude=0.0, temperature_celsius=35.0
        )
        
        response = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "score_available"
        assert data["score"] is not None
        assert data["category"] is not None
        assert data["contributing_factors"] is not None
        
    def test_unknown_zone_returns_404(self):
        response = client.get("/api/zones/unknown-zone/risk")
        assert response.status_code == 404
        
    @patch("app.routes.risk._weather_service.get_current_weather")
    def test_weather_failure_returns_upstream_status(self, mock_weather):
        mock_weather.side_effect = WeatherServiceError("upstream error", status_code=502)
        response = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert response.status_code == 502

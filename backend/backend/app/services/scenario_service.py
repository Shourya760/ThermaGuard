"""
app/services/scenario_service.py

Deterministic intervention and budget scenario engine.
"""

from typing import Dict, Any

from app.schemas.scenario import (
    ScenarioRequest,
    ScenarioResponse,
    InterventionResult,
    InterventionRequest
)
from app.services.zone_service import ZoneService, ZoneNotFoundError


class InvalidInterventionError(ValueError):
    """Raised when an unknown intervention ID is requested."""
    def __init__(self, intervention_id: str):
        self.intervention_id = intervention_id
        super().__init__(f"Unknown intervention: '{intervention_id}'")


class ScenarioService:
    """
    Evaluates requested interventions against a budget.
    """
    VERSION = "1.0"
    
    LIMITATIONS = [
        "Unit costs are illustrative planning assumptions, NOT vendor quotes or verified local market prices.",
        "Quantitative environmental benefits (e.g., exact temperature reduction) are not simulated due to lack of validated baseline data.",
        "Scenarios do not prove a reduction in the Phase 5 heat risk score."
    ]

    # Illustrative dictionary of supported interventions
    INTERVENTIONS_CATALOG = {
        "tree_planting": {
            "name": "Tree Planting (Native Species)",
            "unit": "per tree",
            "cost_inr": 2500.0,
            "qualitative_benefit": "Increases shade coverage and cooling via evapotranspiration over 5-10 years.",
            "limitations": [
                "Assumes sapling cost + initial 1-year maintenance.",
                "Does not provide immediate cooling effect.",
                "Subject to soil and water availability."
            ]
        },
        "shade_structure": {
            "name": "Public Shade Structure",
            "unit": "per square meter",
            "cost_inr": 4500.0,
            "qualitative_benefit": "Provides immediate localized shade, reducing perceived temperature (UTCI).",
            "limitations": [
                "Does not reduce overall ambient air temperature.",
                "Maintenance costs (cleaning, repair) are not included."
            ]
        },
        "cool_roof": {
            "name": "Cool Roof Coating",
            "unit": "per square meter",
            "cost_inr": 350.0,
            "qualitative_benefit": "Reflects solar radiation, reducing indoor temperatures and slightly lowering local Urban Heat Island (UHI).",
            "limitations": [
                "Effectiveness degrades with dust accumulation.",
                "Requires building owner consent."
            ]
        }
    }
    
    def __init__(self):
        self.zone_service = ZoneService()

    def evaluate_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        """
        Evaluate the scenario against the provided budget and zone.
        """
        # 1. Validate the zone exists (will raise ZoneNotFoundError if invalid)
        self.zone_service.get_zone(request.zone_id)
        
        # 2. Evaluate interventions
        evaluated_interventions = []
        total_cost = 0.0
        
        for item in request.interventions:
            if item.intervention_id not in self.INTERVENTIONS_CATALOG:
                raise InvalidInterventionError(item.intervention_id)
                
            catalog_item = self.INTERVENTIONS_CATALOG[item.intervention_id]
            cost = catalog_item["cost_inr"] * item.quantity
            total_cost += cost
            
            evaluated_interventions.append(
                InterventionResult(
                    intervention_id=item.intervention_id,
                    name=catalog_item["name"],
                    quantity_requested=item.quantity,
                    unit=catalog_item["unit"],
                    illustrative_unit_cost_inr=catalog_item["cost_inr"],
                    estimated_cost_inr=round(cost, 2),
                    qualitative_benefit=catalog_item["qualitative_benefit"],
                    limitations=catalog_item["limitations"]
                )
            )
            
        # 3. Calculate budget status
        total_cost = round(total_cost, 2)
        remaining = round(request.budget - total_cost, 2)
        is_feasible = total_cost <= request.budget
        
        return ScenarioResponse(
            zone_id=request.zone_id,
            budget=request.budget,
            total_estimated_cost=total_cost,
            remaining_budget=remaining,
            is_feasible=is_feasible,
            interventions=evaluated_interventions,
            methodology_version=self.VERSION,
            general_limitations=self.LIMITATIONS
        )

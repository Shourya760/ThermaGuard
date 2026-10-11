"""
app/schemas/scenario.py

Pydantic schemas for the intervention and budget scenario engine.
"""

from typing import List, Dict, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class InterventionRequest(BaseModel):
    """
    A requested intervention and its quantity.
    """
    intervention_id: str = Field(
        description="ID of the intervention (e.g., 'tree_planting', 'shade_structure', 'cool_roof')."
    )
    quantity: float = Field(
        description="Amount of the intervention (e.g., number of trees or square meters).",
        gt=0.0
    )


class ScenarioRequest(BaseModel):
    """
    Request to evaluate a set of interventions against a budget for a specific zone.
    """
    zone_id: str = Field(description="The zone identifier where interventions will be applied.")
    budget: float = Field(
        description="Total available budget in INR (₹). Must be greater than 0.",
        gt=0.0
    )
    interventions: List[InterventionRequest] = Field(
        description="List of requested interventions and their quantities.",
        min_length=1
    )

    @field_validator("interventions")
    def check_duplicate_interventions(cls, v):
        seen = set()
        for item in v:
            if item.intervention_id in seen:
                raise ValueError(f"Duplicate intervention_id: '{item.intervention_id}'")
            seen.add(item.intervention_id)
        return v


class InterventionResult(BaseModel):
    """
    Detailed breakdown for a single evaluated intervention.
    """
    intervention_id: str
    name: str
    quantity_requested: float
    unit: str
    illustrative_unit_cost_inr: float
    estimated_cost_inr: float
    qualitative_benefit: str
    limitations: List[str]


class ScenarioResponse(BaseModel):
    """
    Result of evaluating the scenario request.
    """
    zone_id: str
    currency: Literal["INR"] = "INR"
    budget: float
    total_estimated_cost: float
    remaining_budget: float
    is_feasible: bool = Field(
        description="True if total_estimated_cost <= budget, False otherwise."
    )
    
    interventions: List[InterventionResult]
    
    methodology_version: str
    general_limitations: List[str] = Field(
        description="Dataset and methodology limitations applicable to all scenarios."
    )
    
    # We explicitly do NOT return a "new risk score" here, as requested, because 
    # the underlying data is null and we cannot deterministically calculate a risk reduction 
    # without fabricating the environmental baseline and precise cooling effects.

"""
app/schemas/plan.py

Pydantic schemas for action plans.

The ActionPlanCreate schema accepts a ScenarioRequest plus a plan name.
Derived fields (costs, feasibility) are always calculated server-side through
the ScenarioService and are never trusted from the client.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.schemas.scenario import InterventionRequest, InterventionResult


class ActionPlanCreate(BaseModel):
    """
    Input for saving a scenario as a named action plan.
    Client supplies the zone, budget, interventions, and a name.
    All derived cost/feasibility fields are computed server-side.
    """
    name: str = Field(..., description="Non-empty display name for the action plan.")
    zone_id: str = Field(..., description="Zone identifier.")
    budget: float = Field(..., gt=0.0, description="Total available budget in INR.")
    interventions: List[InterventionRequest] = Field(
        ..., min_length=1, description="Interventions to evaluate."
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Plan name must not be empty or whitespace.")
        return v.strip()


class ActionPlanResponse(BaseModel):
    """
    Returned action plan with server-computed cost/feasibility fields.
    """
    id: int
    name: str
    zone_id: str
    budget: float
    total_estimated_cost: float
    remaining_budget: float
    is_feasible: bool
    interventions: List[InterventionResult]
    created_at: datetime

    model_config = {"from_attributes": True}

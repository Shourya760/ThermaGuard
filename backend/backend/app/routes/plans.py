"""
app/routes/plans.py

HTTP routes for Action Plans.

INTEGRITY DESIGN: POST /api/plans accepts a ScenarioRequest + plan name.
It re-runs the scenario through the authoritative ScenarioService so that
total_estimated_cost, remaining_budget, and is_feasible are always server-
computed — the client cannot fabricate or tamper with these values.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import DBActionPlan
from app.schemas.plan import ActionPlanCreate, ActionPlanResponse
from app.schemas.scenario import ScenarioRequest
from app.services.scenario_service import ScenarioService, InvalidInterventionError
from app.services.zone_service import ZoneNotFoundError

router = APIRouter()
_scenario_service = ScenarioService()


@router.post(
    "/api/plans",
    response_model=ActionPlanResponse,
    status_code=201,
    summary="Evaluate a scenario and save it as a named action plan",
    description=(
        "Accepts a zone, budget, and list of interventions (identical to "
        "POST /api/scenarios) plus a non-empty plan name. "
        "The server re-evaluates the scenario through the authoritative "
        "ScenarioService and persists the result. Client-provided cost or "
        "feasibility figures are never trusted."
    ),
)
def create_action_plan(plan: ActionPlanCreate, db: Session = Depends(get_db)):
    """Evaluate and persist a named action plan."""
    # Build an authoritative ScenarioRequest from the validated inputs
    scenario_req = ScenarioRequest(
        zone_id=plan.zone_id,
        budget=plan.budget,
        interventions=plan.interventions,
    )

    # Run through ScenarioService — this validates zone, intervention IDs,
    # and computes all cost/feasibility fields deterministically
    try:
        scenario = _scenario_service.evaluate_scenario(scenario_req)
    except ZoneNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Zone not found: '{exc.zone_id}'.")
    except InvalidInterventionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Persist the authoritative result
    interventions_json = [i.model_dump() for i in scenario.interventions]

    db_plan = DBActionPlan(
        zone_id=scenario.zone_id,
        name=plan.name,
        budget=scenario.budget,
        total_estimated_cost=scenario.total_estimated_cost,
        remaining_budget=scenario.remaining_budget,
        is_feasible=scenario.is_feasible,
        interventions=interventions_json,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get(
    "/api/plans",
    response_model=List[ActionPlanResponse],
    summary="List all saved action plans",
)
def list_action_plans(db: Session = Depends(get_db)):
    """Retrieve all saved action plans."""
    return db.query(DBActionPlan).all()

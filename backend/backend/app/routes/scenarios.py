"""
app/routes/scenarios.py

HTTP routes for the intervention and budget scenario engine.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.services.scenario_service import ScenarioService, InvalidInterventionError
from app.services.zone_service import ZoneNotFoundError

router = APIRouter()
_scenario_service = ScenarioService()


@router.get(
    "/api/interventions",
    summary="List interventions supported by the scenario engine",
    description="Returns the server-owned catalog used to validate and price scenario requests.",
)
def list_interventions():
    return [
        {
            "id": intervention_id,
            "name": item["name"],
            "unit": item["unit"],
            "unit_cost_inr": item["cost_inr"],
            "qualitative_benefit": item["qualitative_benefit"],
            "limitations": item["limitations"],
        }
        for intervention_id, item in _scenario_service.INTERVENTIONS_CATALOG.items()
    ]

@router.post(
    "/api/scenarios",
    response_model=ScenarioResponse,
    summary="Evaluate an intervention scenario against a budget",
    description=(
        "Calculates the estimated cost and feasibility of a set of interventions "
        "applied to a specific zone. Costs are illustrative and qualitative benefits "
        "are returned instead of fabricated numerical risk reductions."
    )
)
def evaluate_scenario(request: ScenarioRequest) -> ScenarioResponse:
    """Evaluate budget feasibility of requested interventions."""
    try:
        return _scenario_service.evaluate_scenario(request)
    except ZoneNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Zone not found: '{exc.zone_id}'."
        )
    except InvalidInterventionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

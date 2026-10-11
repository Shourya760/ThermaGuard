"""
app/routes/risk.py

HTTP route for the explainable heat-risk engine.
"""

from fastapi import APIRouter, HTTPException, Path

from app.schemas.risk import RiskResponse
from app.services.zone_service import ZoneService, ZoneNotFoundError
from app.services.weather_service import WeatherService, WeatherServiceError
from app.services.risk_service import RiskService

router = APIRouter()

_zone_service = ZoneService()
_weather_service = WeatherService()
_risk_service = RiskService()


@router.get(
    "/api/zones/{zone_id}/risk",
    response_model=RiskResponse,
    summary="Get explainable heat risk for a zone",
    description=(
        "Returns a deterministic heat risk evaluation for a specific zone based on "
        "real-time weather and static zone indicators. If data is insufficient (e.g. "
        "missing satellite indicators), it will return a status of 'insufficient_data' "
        "and a null score, rather than guessing."
    ),
)
def get_zone_risk(
    zone_id: str = Path(
        ...,
        description="Zone identifier slug (e.g. 'delhi-connaught-place').",
        min_length=1,
    ),
) -> RiskResponse:
    """Calculate heat risk for a given zone."""
    
    # 1. Fetch the zone
    try:
        zone = _zone_service.get_zone(zone_id)
    except ZoneNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Zone not found: '{exc.zone_id}'."
        )
        
    # 2. Fetch the weather for that zone
    try:
        weather = _weather_service.get_current_weather(lat=zone.latitude, lon=zone.longitude)
    except WeatherServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"Could not retrieve weather for risk calculation: {exc.message}"
        )
        
    # 3. Calculate risk
    try:
        return _risk_service.calculate_risk(zone, weather)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

"""
app/routes/zones.py

HTTP routes for zone data.

GET /api/zones          → list all zones (compact ZoneSummary)
GET /api/zones/{zone_id} → full ZoneDetail for one zone

The route handlers are deliberately thin: receive the request, call the
service, translate errors to HTTP responses. No business logic lives here.
"""

from fastapi import APIRouter, HTTPException, Path
from typing import List

from app.services.zone_service import ZoneService, ZoneNotFoundError
from app.schemas.zone import ZoneSummary, ZoneDetail

router = APIRouter()

# One shared service instance for this module.
_zone_service = ZoneService()


@router.get(
    "/api/zones",
    response_model=List[ZoneSummary],
    summary="List all pilot zones",
    description=(
        "Returns a compact list of all zones in the pilot dataset. "
        "All current zones are labelled data_status='DEMO' — they contain "
        "verified geographic coordinates but no satellite-derived heat indicators. "
        "Use GET /api/zones/{zone_id} for the full record including provenance details."
    ),
)
def list_zones() -> List[ZoneSummary]:
    """Return compact summaries of all available zones."""
    return _zone_service.list_zones()


@router.get(
    "/api/zones/{zone_id}",
    response_model=ZoneDetail,
    summary="Get full details for a single zone",
    description=(
        "Returns the complete zone record including geographic coordinates, "
        "land-use description, data provenance, freshness timestamp, and "
        "heat indicator fields. "
        "Heat indicator fields (LST, vegetation, shade, vulnerability) are "
        "currently null — see heat_indicators.missing_data_reason for context."
    ),
)
def get_zone(
    zone_id: str = Path(
        ...,
        description="Zone identifier slug (e.g. 'delhi-connaught-place').",
        min_length=1,
    ),
) -> ZoneDetail:
    """Return the full ZoneDetail for a single zone by ID."""
    try:
        return _zone_service.get_zone(zone_id)
    except ZoneNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Zone not found: '{exc.zone_id}'. "
                   f"Use GET /api/zones to see available zone IDs.",
        )

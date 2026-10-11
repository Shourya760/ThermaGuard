"""
app/services/zone_service.py

Loads the pilot zone dataset from app/data/demo_zones.json and provides
methods to list zones and retrieve a single zone by ID.

No database is used in Phase 4. The JSON file is loaded once at module
import time and kept in memory. This is intentional for the hackathon MVP;
Phase 7 will migrate to SQLAlchemy + SQLite.

Design decisions:
- The raw JSON is validated into Pydantic models on load so bad data is
  caught immediately at startup, not silently at request time.
- ZoneNotFoundError is a custom exception so the route layer can translate
  it to a clean 404 without exposing internal details.
- No heat-risk scoring happens here; that belongs to Phase 5.
"""

import json
from pathlib import Path
from typing import List

from app.schemas.zone import ZoneDetail, ZoneSummary, HeatIndicators


# ─── Custom exception ─────────────────────────────────────────────────────────

class ZoneNotFoundError(Exception):
    """Raised when a requested zone ID does not exist in the dataset."""

    def __init__(self, zone_id: str):
        super().__init__(f"Zone '{zone_id}' not found.")
        self.zone_id = zone_id


# ─── Data loading ─────────────────────────────────────────────────────────────

_DATA_FILE = Path(__file__).parent.parent / "data" / "demo_zones.json"


def _load_zones() -> dict[str, ZoneDetail]:
    """
    Load demo_zones.json and parse each zone into a ZoneDetail model.
    Returns a dict keyed by zone ID for O(1) lookup.

    Called once at module import time.
    """
    with _DATA_FILE.open(encoding="utf-8") as f:
        raw = json.load(f)

    zones: dict[str, ZoneDetail] = {}
    for entry in raw["zones"]:
        # Build the nested HeatIndicators model from the JSON sub-dict
        indicators_raw = entry.get("heat_indicators", {})
        indicators = HeatIndicators(**indicators_raw)

        zone = ZoneDetail(
            id=entry["id"],
            name=entry["name"],
            city=entry["city"],
            state=entry.get("state"),
            country=entry["country"],
            latitude=entry["latitude"],
            longitude=entry["longitude"],
            area_type=entry["area_type"],
            description=entry["description"],
            coordinate_source=entry["coordinate_source"],
            data_provenance=entry["data_provenance"],
            data_status=entry["data_status"],
            last_verified_utc=entry.get("last_verified_utc"),
            heat_indicators=indicators,
        )
        zones[zone.id] = zone

    return zones


# Module-level cache — loaded once, reused for every request.
_ZONES: dict[str, ZoneDetail] = _load_zones()


# ─── Service ──────────────────────────────────────────────────────────────────

class ZoneService:
    """
    Provides access to the pilot zone dataset.

    Methods:
        list_zones()     → list of ZoneSummary (compact, for the list endpoint)
        get_zone(id)     → ZoneDetail (full record, raises ZoneNotFoundError)
    """

    def list_zones(self) -> List[ZoneSummary]:
        """
        Return a compact summary of every zone in the dataset.
        Ordered by zone ID (alphabetical) for stable, predictable responses.
        """
        return [
            ZoneSummary(
                id=zone.id,
                name=zone.name,
                city=zone.city,
                country=zone.country,
                latitude=zone.latitude,
                longitude=zone.longitude,
                area_type=zone.area_type,
                data_status=zone.data_status,
            )
            for zone in sorted(_ZONES.values(), key=lambda z: z.id)
        ]

    def get_zone(self, zone_id: str) -> ZoneDetail:
        """
        Return the full ZoneDetail for a given zone ID.

        Args:
            zone_id: The slug identifier for the zone (e.g. 'delhi-connaught-place').

        Returns:
            ZoneDetail with all fields populated (heat indicators may be null).

        Raises:
            ZoneNotFoundError: If zone_id is not present in the dataset.
        """
        zone = _ZONES.get(zone_id)
        if zone is None:
            raise ZoneNotFoundError(zone_id)
        return zone

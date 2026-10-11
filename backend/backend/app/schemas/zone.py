"""
app/schemas/zone.py

Pydantic schemas for zone-related endpoints.

HeatIndicators
    Holds satellite-derived and socio-economic fields that may be null.
    Each null field has a corresponding 'missing_data_reason' explaining
    why the value is absent — we never fabricate indicator values.

ZoneSummary
    Lightweight schema returned by GET /api/zones (the list endpoint).
    Omits heavy indicator data to keep the list response compact.

ZoneDetail
    Full schema returned by GET /api/zones/{zone_id}.
    Includes provenance, freshness, and all heat indicator fields.

DataStatus (literal)
    Marks whether zone data is "DEMO" (illustrative) or "VERIFIED"
    (sourced from a validated external dataset). Currently all zones
    are "DEMO" for the hackathon MVP.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class HeatIndicators(BaseModel):
    """
    Environmental and demographic indicators for a zone.

    All numeric fields are Optional because reliable values require
    satellite imagery (Landsat/MODIS) or validated socio-economic datasets
    that have not yet been sourced.

    IMPORTANT: These fields MUST NOT be populated with estimated or
    illustrative numbers. They should only ever hold null or a value
    traceable to a verified, cited source.
    """

    land_surface_temperature_celsius: Optional[float] = Field(
        default=None,
        description=(
            "Daytime land-surface temperature in Celsius derived from "
            "satellite imagery (e.g. Landsat LST). "
            "NOT interchangeable with air temperature. "
            "Null until satellite data is sourced."
        ),
    )
    vegetation_coverage_percent: Optional[float] = Field(
        default=None,
        description=(
            "Estimated percentage of zone area covered by vegetation "
            "(trees, grass, shrubs). "
            "Null until NDVI or land-cover data is sourced."
        ),
    )
    shade_coverage_percent: Optional[float] = Field(
        default=None,
        description=(
            "Estimated percentage of public space with shade coverage "
            "(tree canopy + built shade structures). "
            "Null until field survey or remote sensing data is available."
        ),
    )
    population_vulnerability_index: Optional[float] = Field(
        default=None,
        description=(
            "Composite index (0–1) representing relative population "
            "vulnerability to heat (e.g. elderly, outdoor workers, "
            "low-income households). "
            "Null until validated socio-economic data is sourced."
        ),
    )
    missing_data_reason: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of why indicator fields are null.",
    )


class ZoneSummary(BaseModel):
    """
    Compact zone record for list responses.
    Does not include full heat indicators to keep the payload small.
    """

    id: str = Field(description="Unique zone identifier (slug).")
    name: str = Field(description="Human-readable zone name.")
    city: str
    country: str
    latitude: float
    longitude: float
    area_type: str = Field(
        description=(
            "Broad land-use category: commercial, residential, "
            "industrial, green_space, dense_urban_residential, etc."
        )
    )
    data_status: Literal["DEMO", "VERIFIED"] = Field(
        description=(
            "'DEMO' = illustrative/sample data for the hackathon MVP. "
            "'VERIFIED' = sourced from a validated external dataset."
        )
    )


class ZoneDetail(BaseModel):
    """
    Full zone record returned by GET /api/zones/{zone_id}.
    Includes provenance, freshness, and all heat-indicator fields.
    """

    id: str
    name: str
    city: str
    state: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    area_type: str
    description: str = Field(description="Qualitative description of the zone.")

    # --- Provenance & freshness ---
    coordinate_source: str = Field(
        description="Where the lat/lon coordinates were obtained from."
    )
    data_provenance: str = Field(
        description="Sources for land-use classification and other metadata."
    )
    data_status: Literal["DEMO", "VERIFIED"]
    last_verified_utc: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp of the last data verification.",
    )

    # --- Heat indicators (all nullable — see HeatIndicators docstring) ---
    heat_indicators: HeatIndicators

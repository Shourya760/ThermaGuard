"""
app/schemas/weather.py

Pydantic schemas for the weather endpoint.

WeatherResponse is what GET /api/weather returns.
All fields that may be unavailable from the upstream API are Optional.
We never fabricate values; missing data is returned as null.
"""

from typing import Optional
from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    """
    Current weather observation for a given latitude/longitude.

    Data source: Open-Meteo (https://open-meteo.com/)
    All temperature values are in Celsius.
    Humidity is in percent.
    Observation time is in UTC (ISO 8601 string as returned by the API).
    """

    source: str = Field(
        default="Open-Meteo (https://open-meteo.com/)",
        description="Data provider attribution.",
    )
    latitude: float = Field(description="Requested latitude (decimal degrees).")
    longitude: float = Field(description="Requested longitude (decimal degrees).")

    # Observation timestamp returned by Open-Meteo (UTC).
    # The field is named 'time' in their response.
    observation_time: Optional[str] = Field(
        default=None,
        description="UTC timestamp of the observation (ISO 8601), or null if unavailable.",
    )

    # --- Observed values (all Optional; null means 'not available') ---
    temperature_celsius: Optional[float] = Field(
        default=None,
        description="Air temperature at 2 m above ground (°C).",
    )
    apparent_temperature_celsius: Optional[float] = Field(
        default=None,
        description="Apparent (feels-like) temperature (°C).",
    )
    relative_humidity_percent: Optional[float] = Field(
        default=None,
        description="Relative humidity at 2 m above ground (%).",
    )

    # --- Unit metadata (from the Open-Meteo 'current_units' block) ---
    units: dict = Field(
        default_factory=dict,
        description="Unit strings for each returned variable, as reported by Open-Meteo.",
    )

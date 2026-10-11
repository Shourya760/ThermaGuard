"""
app/routes/weather.py

HTTP route for GET /api/weather.

The route handler is deliberately thin:
  1. Receive and validate query parameters via FastAPI's Query().
  2. Delegate to WeatherService.
  3. Translate WeatherServiceError into the appropriate HTTP error response.

No business logic lives here.
"""

from fastapi import APIRouter, Query, HTTPException
from app.services.weather_service import WeatherService, WeatherServiceError
from app.schemas.weather import WeatherResponse

router = APIRouter()

# One shared service instance for this module.
# Each request reuses it; the underlying httpx.get() opens a fresh connection.
_weather_service = WeatherService()


@router.get(
    "/api/weather",
    response_model=WeatherResponse,
    summary="Current weather for a location",
    description=(
        "Returns current temperature, apparent temperature, and relative "
        "humidity from Open-Meteo for the supplied coordinates. "
        "All observation fields may be null if the upstream API does not "
        "return them — no values are fabricated."
    ),
)
def get_weather(
    lat: float = Query(
        ...,
        description="Latitude in decimal degrees (-90 to 90).",
        ge=-90.0,
        le=90.0,
    ),
    lon: float = Query(
        ...,
        description="Longitude in decimal degrees (-180 to 180).",
        ge=-180.0,
        le=180.0,
    ),
) -> WeatherResponse:
    """
    Fetch and return current weather data for the given coordinates.

    FastAPI validates the `ge`/`le` constraints before this function is called,
    so by the time we reach WeatherService the values are already in range.
    The service performs its own internal validation as an extra safety net.
    """
    try:
        return _weather_service.get_current_weather(lat=lat, lon=lon)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

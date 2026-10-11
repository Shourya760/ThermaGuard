"""
app/services/weather_service.py

Fetches current weather data from Open-Meteo's free, no-auth API.

Open-Meteo endpoint used:
  https://api.open-meteo.com/v1/forecast
  Parameters: latitude, longitude, current=[temperature_2m,
              relative_humidity_2m, apparent_temperature]

Design decisions:
- A single HTTPX client is created per WeatherService instance with a
  configurable timeout so the API call never hangs the server.
- If the upstream call fails for ANY reason (network error, bad status,
  malformed JSON, missing keys) we raise a WeatherServiceError with a
  clear message rather than returning fake data.
- Callers (the route handler) catch WeatherServiceError and return the
  appropriate HTTP error response.
- Latitude must be -90 ≤ lat ≤ 90; longitude must be -180 ≤ lon ≤ 180.
  Validation happens here so the rule is enforced regardless of how the
  service is called.
"""

import httpx

from app.schemas.weather import WeatherResponse


# ─── Custom exception ─────────────────────────────────────────────────────────

class WeatherServiceError(Exception):
    """
    Raised when the WeatherService cannot return a valid observation.

    Attributes:
        message  – human-readable description suitable for an API error body.
        status_code – suggested HTTP status code for the caller to use.
    """

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ─── Open-Meteo constants ─────────────────────────────────────────────────────

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# The exact variable names Open-Meteo uses in its JSON response.
CURRENT_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
]


# ─── Service ──────────────────────────────────────────────────────────────────

class WeatherService:
    """
    Thin wrapper around the Open-Meteo current-weather API.

    Usage:
        service = WeatherService()
        result = service.get_current_weather(lat=28.6, lon=77.2)
        # result is a WeatherResponse Pydantic model.
    """

    def __init__(self, timeout_seconds: float = 10.0):
        """
        Args:
            timeout_seconds: Maximum seconds to wait for Open-Meteo to respond.
                             Keeps requests from hanging the server indefinitely.
        """
        self._timeout = timeout_seconds

    # ------------------------------------------------------------------
    # Coordinate validation (static — no HTTP involved)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_coordinates(lat: float, lon: float) -> None:
        """
        Raises WeatherServiceError (HTTP 422) for coordinates that are
        outside physically valid ranges.

        Valid ranges:
          latitude  : -90  to +90
          longitude : -180 to +180
        """
        if not (-90.0 <= lat <= 90.0):
            raise WeatherServiceError(
                f"Latitude {lat} is out of range. Must be between -90 and 90.",
                status_code=422,
            )
        if not (-180.0 <= lon <= 180.0):
            raise WeatherServiceError(
                f"Longitude {lon} is out of range. Must be between -180 and 180.",
                status_code=422,
            )

    # ------------------------------------------------------------------
    # Main public method
    # ------------------------------------------------------------------

    def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        """
        Fetch current weather for the given coordinates from Open-Meteo.

        Args:
            lat: Latitude in decimal degrees (-90 to 90).
            lon: Longitude in decimal degrees (-180 to 180).

        Returns:
            WeatherResponse with available fields populated.
            Fields that the API does not return are set to None.

        Raises:
            WeatherServiceError: For invalid coordinates, network failures,
                                 non-200 HTTP responses, or unparseable data.
        """
        self._validate_coordinates(lat, lon)

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join(CURRENT_VARIABLES),
            "timezone": "UTC",
        }

        # --- Make the HTTP request ---
        try:
            response = httpx.get(
                OPEN_METEO_URL,
                params=params,
                timeout=self._timeout,
            )
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Open-Meteo did not respond within the timeout period.",
                status_code=504,
            )
        except httpx.RequestError as exc:
            raise WeatherServiceError(
                f"Could not reach Open-Meteo: {exc}",
                status_code=502,
            )

        # --- Check HTTP status ---
        if response.status_code != 200:
            raise WeatherServiceError(
                f"Open-Meteo returned an unexpected status: {response.status_code}.",
                status_code=502,
            )

        # --- Parse JSON ---
        try:
            data = response.json()
        except Exception:
            raise WeatherServiceError(
                "Open-Meteo returned a response that could not be parsed as JSON.",
                status_code=502,
            )

        # --- Extract fields (gracefully handle missing keys) ---
        current_block = data.get("current", {})
        units_block = data.get("current_units", {})

        if not isinstance(current_block, dict):
            raise WeatherServiceError(
                "Open-Meteo response is missing the expected 'current' data block.",
                status_code=502,
            )

        # Map Open-Meteo field names → our schema field names.
        # We use .get() so a missing field becomes None, never a KeyError.
        temperature = current_block.get("temperature_2m")          # °C
        humidity    = current_block.get("relative_humidity_2m")    # %
        apparent    = current_block.get("apparent_temperature")    # °C
        obs_time    = current_block.get("time")                    # ISO 8601 UTC

        return WeatherResponse(
            latitude=lat,
            longitude=lon,
            observation_time=obs_time,
            temperature_celsius=temperature,
            apparent_temperature_celsius=apparent,
            relative_humidity_percent=humidity,
            units=units_block if isinstance(units_block, dict) else {},
        )

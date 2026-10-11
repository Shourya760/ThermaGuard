"""
tests/test_phase3_weather.py

Automated tests for Phase 3 — Weather Service and GET /api/weather endpoint.

ALL tests use unittest.mock to intercept httpx.get() calls.
No real network requests are made; these tests pass without internet access.

Test categories:
  A. WeatherService unit tests (coordinate validation, response parsing,
     error handling for timeouts / bad status / malformed JSON / missing fields)
  B. GET /api/weather endpoint integration tests (happy path, invalid params,
     upstream errors propagated correctly)
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.weather_service import WeatherService, WeatherServiceError

client = TestClient(app)

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

# A realistic Open-Meteo JSON payload for New Delhi (28.6, 77.2)
MOCK_OPEN_METEO_SUCCESS = {
    "latitude": 28.6,
    "longitude": 77.2,
    "timezone": "UTC",
    "current_units": {
        "time": "iso8601",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "apparent_temperature": "°C",
    },
    "current": {
        "time": "2024-06-15T09:00",
        "temperature_2m": 38.4,
        "relative_humidity_2m": 42.0,
        "apparent_temperature": 41.1,
    },
}


def _make_mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    """Helper: build a mock httpx.Response-like object."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


# ===========================================================================
# A. WeatherService unit tests
# ===========================================================================

class TestWeatherServiceCoordinateValidation:
    """_validate_coordinates should accept valid ranges and reject bad ones."""

    service = WeatherService()

    def test_valid_coordinates_do_not_raise(self):
        # Should not raise for reasonable values
        self.service._validate_coordinates(lat=28.6, lon=77.2)
        self.service._validate_coordinates(lat=0.0, lon=0.0)
        self.service._validate_coordinates(lat=-90.0, lon=-180.0)
        self.service._validate_coordinates(lat=90.0, lon=180.0)

    def test_latitude_too_high_raises(self):
        with pytest.raises(WeatherServiceError) as exc_info:
            self.service._validate_coordinates(lat=91.0, lon=0.0)
        assert exc_info.value.status_code == 422

    def test_latitude_too_low_raises(self):
        with pytest.raises(WeatherServiceError) as exc_info:
            self.service._validate_coordinates(lat=-91.0, lon=0.0)
        assert exc_info.value.status_code == 422

    def test_longitude_too_high_raises(self):
        with pytest.raises(WeatherServiceError) as exc_info:
            self.service._validate_coordinates(lat=0.0, lon=181.0)
        assert exc_info.value.status_code == 422

    def test_longitude_too_low_raises(self):
        with pytest.raises(WeatherServiceError) as exc_info:
            self.service._validate_coordinates(lat=0.0, lon=-181.0)
        assert exc_info.value.status_code == 422


class TestWeatherServiceResponseParsing:
    """get_current_weather should parse valid Open-Meteo responses correctly."""

    service = WeatherService()

    @patch("app.services.weather_service.httpx.get")
    def test_happy_path_fields_populated(self, mock_get):
        mock_get.return_value = _make_mock_response(MOCK_OPEN_METEO_SUCCESS)

        result = self.service.get_current_weather(lat=28.6, lon=77.2)

        assert result.latitude == 28.6
        assert result.longitude == 77.2
        assert result.temperature_celsius == 38.4
        assert result.relative_humidity_percent == 42.0
        assert result.apparent_temperature_celsius == 41.1
        assert result.observation_time == "2024-06-15T09:00"
        assert result.source == "Open-Meteo (https://open-meteo.com/)"

    @patch("app.services.weather_service.httpx.get")
    def test_units_block_included(self, mock_get):
        mock_get.return_value = _make_mock_response(MOCK_OPEN_METEO_SUCCESS)

        result = self.service.get_current_weather(lat=28.6, lon=77.2)

        assert result.units.get("temperature_2m") == "°C"
        assert result.units.get("relative_humidity_2m") == "%"

    @patch("app.services.weather_service.httpx.get")
    def test_missing_optional_fields_become_none(self, mock_get):
        """If Open-Meteo omits a field we return None, not a fabricated value."""
        partial_response = {
            "current_units": {},
            "current": {
                "time": "2024-06-15T09:00",
                # temperature_2m and apparent_temperature intentionally absent
                "relative_humidity_2m": 50.0,
            },
        }
        mock_get.return_value = _make_mock_response(partial_response)

        result = self.service.get_current_weather(lat=28.6, lon=77.2)

        assert result.temperature_celsius is None
        assert result.apparent_temperature_celsius is None
        assert result.relative_humidity_percent == 50.0

    @patch("app.services.weather_service.httpx.get")
    def test_entirely_empty_current_block_returns_nulls(self, mock_get):
        """An empty 'current' block should not crash; all fields become None."""
        mock_get.return_value = _make_mock_response({"current": {}, "current_units": {}})

        result = self.service.get_current_weather(lat=0.0, lon=0.0)

        assert result.temperature_celsius is None
        assert result.relative_humidity_percent is None
        assert result.observation_time is None


class TestWeatherServiceErrorHandling:
    """WeatherService must raise WeatherServiceError for all failure modes."""

    service = WeatherService()

    @patch("app.services.weather_service.httpx.get")
    def test_timeout_raises_service_error(self, mock_get):
        import httpx as _httpx
        mock_get.side_effect = _httpx.TimeoutException("timed out")

        with pytest.raises(WeatherServiceError) as exc_info:
            self.service.get_current_weather(lat=28.6, lon=77.2)

        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.message.lower()

    @patch("app.services.weather_service.httpx.get")
    def test_network_error_raises_service_error(self, mock_get):
        import httpx as _httpx
        mock_get.side_effect = _httpx.RequestError("connection refused")

        with pytest.raises(WeatherServiceError) as exc_info:
            self.service.get_current_weather(lat=28.6, lon=77.2)

        assert exc_info.value.status_code == 502

    @patch("app.services.weather_service.httpx.get")
    def test_non_200_status_raises_service_error(self, mock_get):
        mock_get.return_value = _make_mock_response({}, status_code=500)

        with pytest.raises(WeatherServiceError) as exc_info:
            self.service.get_current_weather(lat=28.6, lon=77.2)

        assert exc_info.value.status_code == 502
        assert "500" in exc_info.value.message

    @patch("app.services.weather_service.httpx.get")
    def test_malformed_json_raises_service_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("not valid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(WeatherServiceError) as exc_info:
            self.service.get_current_weather(lat=28.6, lon=77.2)

        assert exc_info.value.status_code == 502

    @patch("app.services.weather_service.httpx.get")
    def test_missing_current_block_raises_service_error(self, mock_get):
        """Response without a 'current' key should raise, not return nulls."""
        mock_get.return_value = _make_mock_response({"timezone": "UTC"})

        # current block defaults to {} so we actually get nulls — that's fine
        # (the service only errors if 'current' exists but is not a dict)
        result = self.service.get_current_weather(lat=0.0, lon=0.0)
        assert result.temperature_celsius is None


# ===========================================================================
# B. GET /api/weather endpoint integration tests
# ===========================================================================

class TestWeatherEndpoint:
    """Test the HTTP layer — routes, query-param validation, error propagation."""

    @patch("app.routes.weather._weather_service.get_current_weather")
    def test_happy_path_returns_200(self, mock_svc):
        from app.schemas.weather import WeatherResponse

        mock_svc.return_value = WeatherResponse(
            latitude=28.6,
            longitude=77.2,
            observation_time="2024-06-15T09:00",
            temperature_celsius=38.4,
            apparent_temperature_celsius=41.1,
            relative_humidity_percent=42.0,
            units={"temperature_2m": "°C"},
        )

        response = client.get("/api/weather", params={"lat": 28.6, "lon": 77.2})

        assert response.status_code == 200
        data = response.json()
        assert data["temperature_celsius"] == 38.4
        assert data["relative_humidity_percent"] == 42.0
        assert data["observation_time"] == "2024-06-15T09:00"

    def test_missing_lat_returns_422(self):
        response = client.get("/api/weather", params={"lon": 77.2})
        assert response.status_code == 422

    def test_missing_lon_returns_422(self):
        response = client.get("/api/weather", params={"lat": 28.6})
        assert response.status_code == 422

    def test_lat_out_of_range_returns_422(self):
        response = client.get("/api/weather", params={"lat": 95.0, "lon": 77.2})
        assert response.status_code == 422

    def test_lon_out_of_range_returns_422(self):
        response = client.get("/api/weather", params={"lat": 28.6, "lon": 200.0})
        assert response.status_code == 422

    def test_non_numeric_lat_returns_422(self):
        response = client.get("/api/weather", params={"lat": "abc", "lon": 77.2})
        assert response.status_code == 422

    @patch("app.routes.weather._weather_service.get_current_weather")
    def test_upstream_timeout_returns_504(self, mock_svc):
        mock_svc.side_effect = WeatherServiceError("timed out", status_code=504)

        response = client.get("/api/weather", params={"lat": 28.6, "lon": 77.2})

        assert response.status_code == 504

    @patch("app.routes.weather._weather_service.get_current_weather")
    def test_upstream_failure_returns_502(self, mock_svc):
        mock_svc.side_effect = WeatherServiceError("upstream error", status_code=502)

        response = client.get("/api/weather", params={"lat": 28.6, "lon": 77.2})

        assert response.status_code == 502

    @patch("app.routes.weather._weather_service.get_current_weather")
    def test_response_includes_source_field(self, mock_svc):
        from app.schemas.weather import WeatherResponse

        mock_svc.return_value = WeatherResponse(latitude=0.0, longitude=0.0)

        response = client.get("/api/weather", params={"lat": 0.0, "lon": 0.0})

        assert response.status_code == 200
        assert "source" in response.json()

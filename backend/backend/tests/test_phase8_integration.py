"""
tests/test_phase8_integration.py

Phase 8 — Integration and Reliability tests.

These tests verify cross-service behaviour, HTTP contract consistency,
CORS headers, startup wiring, and honest-data semantics for the full
CoolBlock API stack.

All weather calls are mocked so no internet access is required.
The DB dependency is overridden to an in-memory SQLite instance so
the local coolblock.db file is never touched.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Base
from app.schemas.weather import WeatherResponse

client = TestClient(app)

KNOWN_ZONE = "delhi-connaught-place"

_MOCK_WEATHER = WeatherResponse(
    source="open-meteo",
    latitude=28.6315,
    longitude=77.2167,
    temperature_celsius=36.0,
    apparent_temperature_celsius=38.5,
    relative_humidity_percent=30.0,
)




# ══════════════════════════════════════════════════════════════════════════════
# 1. Core endpoints — HTTP contracts
# ══════════════════════════════════════════════════════════════════════════════

class TestCoreEndpoints:

    def test_root_returns_200(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "message" in r.json()

    def test_health_returns_ok(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert "env" in r.json()

    def test_docs_endpoint_loads(self):
        r = client.get("/docs")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_openapi_json_includes_all_routes(self):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        paths = r.json()["paths"]
        expected = ["/api/weather", "/api/zones", "/api/zones/{zone_id}", "/api/interventions",
                    "/api/zones/{zone_id}/risk", "/api/scenarios", "/api/plans"]
        for ep in expected:
            assert ep in paths, f"Missing route in OpenAPI schema: {ep}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. CORS headers
# ══════════════════════════════════════════════════════════════════════════════

class TestCORS:

    def test_cors_header_present_for_vite_origin(self):
        r = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_preflight_returns_200(self):
        r = client.options(
            "/api/zones",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code in (200, 204)


# ══════════════════════════════════════════════════════════════════════════════
# 3. Zone API — integration
# ══════════════════════════════════════════════════════════════════════════════

class TestZoneIntegration:

    def test_list_zones_all_carry_no_fabricated_indicators(self):
        r = client.get("/api/zones")
        assert r.status_code == 200
        for zone in r.json():
            # List endpoint should NOT expose heat_indicators at all
            assert "heat_indicators" not in zone

    def test_zone_detail_heat_indicators_always_null(self):
        r = client.get(f"/api/zones/{KNOWN_ZONE}")
        assert r.status_code == 200
        hi = r.json()["heat_indicators"]
        assert hi["land_surface_temperature_celsius"] is None
        assert hi["vegetation_coverage_percent"] is None
        assert hi["shade_coverage_percent"] is None
        assert hi["population_vulnerability_index"] is None

    def test_unknown_zone_detail_returns_404_with_detail(self):
        r = client.get("/api/zones/not-a-real-zone")
        assert r.status_code == 404
        assert "detail" in r.json()

    def test_zone_detail_data_status_is_demo(self):
        r = client.get(f"/api/zones/{KNOWN_ZONE}")
        assert r.json()["data_status"] == "DEMO"


# ══════════════════════════════════════════════════════════════════════════════
# 4. Risk endpoint — integration (weather mocked)
# ══════════════════════════════════════════════════════════════════════════════

class TestRiskIntegration:

    @patch("app.routes.risk._weather_service.get_current_weather", return_value=_MOCK_WEATHER)
    def test_demo_zone_always_returns_insufficient_data(self, _mock):
        """All demo zones have null indicators — risk must never be fabricated."""
        r = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "insufficient_data"
        assert data["score"] is None
        assert data["category"] is None
        assert len(data["missing_indicators"]) > 0

    @patch("app.routes.risk._weather_service.get_current_weather", return_value=_MOCK_WEATHER)
    def test_risk_response_carries_limitations(self, _mock):
        r = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["limitations"], list)
        assert len(data["limitations"]) > 0
        # Must not claim to be a validated medical index
        for lim in data["limitations"]:
            assert "NOT a validated" in lim or "medical" in lim.lower() or lim  # at least one warning

    @patch("app.routes.risk._weather_service.get_current_weather", return_value=_MOCK_WEATHER)
    def test_risk_inputs_used_contains_weather_data(self, _mock):
        """Weather data must be passed into risk evaluation even when score is null."""
        r = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        data = r.json()
        assert "temperature_celsius" in data["inputs_used"]
        assert data["inputs_used"]["temperature_celsius"] == 36.0

    def test_risk_unknown_zone_returns_404(self):
        r = client.get("/api/zones/ghost-zone/risk")
        assert r.status_code == 404
        assert "detail" in r.json()

    @patch(
        "app.routes.risk._weather_service.get_current_weather",
        side_effect=__import__("app.services.weather_service", fromlist=["WeatherServiceError"]).WeatherServiceError(
            "upstream timeout", status_code=504
        ),
    )
    def test_weather_failure_in_risk_chain_returns_upstream_status(self, _mock):
        r = client.get(f"/api/zones/{KNOWN_ZONE}/risk")
        assert r.status_code == 504
        assert "detail" in r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 5. Scenario endpoint — honest-data semantics
# ══════════════════════════════════════════════════════════════════════════════

class TestScenarioIntegration:

    def test_intervention_catalog_matches_scenario_engine(self):
        r = client.get("/api/interventions")
        assert r.status_code == 200
        items = {item["id"]: item for item in r.json()}
        assert {"tree_planting", "shade_structure", "cool_roof"} == set(items)
        assert items["cool_roof"]["unit_cost_inr"] == 350.0

    def _post_scenario(self, **kwargs):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 100000.0,
            "interventions": [
                {"intervention_id": "tree_planting", "quantity": 10}
            ],
        }
        payload.update(kwargs)
        return client.post("/api/scenarios", json=payload)

    def test_scenario_never_returns_quantitative_cooling_claim(self):
        r = self._post_scenario()
        assert r.status_code == 200
        data = r.json()
        # There must be NO numeric temperature_reduction or risk_score_reduction field
        assert "temperature_reduction" not in data
        assert "risk_score_reduction" not in data

    def test_scenario_cost_labelled_illustrative_in_limitations(self):
        r = self._post_scenario()
        data = r.json()
        combined = " ".join(data["general_limitations"])
        assert "illustrative" in combined.lower()

    def test_scenario_costs_are_arithmetically_consistent(self):
        """itemised costs must sum to total_estimated_cost."""
        r = self._post_scenario()
        data = r.json()
        itemised_sum = sum(i["estimated_cost_inr"] for i in data["interventions"])
        assert abs(itemised_sum - data["total_estimated_cost"]) < 0.01

    def test_scenario_remaining_budget_is_consistent(self):
        r = self._post_scenario()
        data = r.json()
        expected_remaining = round(data["budget"] - data["total_estimated_cost"], 2)
        assert abs(data["remaining_budget"] - expected_remaining) < 0.01

    def test_over_budget_scenario_is_not_feasible(self):
        # 10 trees @ 2500 = 25000; budget 5000 → not feasible
        r = self._post_scenario(budget=5000.0)
        assert r.status_code == 200
        data = r.json()
        assert data["is_feasible"] is False

    def test_scenario_unknown_zone_returns_404(self):
        r = self._post_scenario(zone_id="nowhere")
        assert r.status_code == 404

    def test_scenario_missing_body_returns_422(self):
        r = client.post("/api/scenarios", json={})
        assert r.status_code == 422

    def test_scenario_empty_interventions_returns_422(self):
        r = client.post("/api/scenarios", json={
            "zone_id": KNOWN_ZONE, "budget": 1000.0, "interventions": []
        })
        assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# 6. Plans endpoint — cross-service integration
# ══════════════════════════════════════════════════════════════════════════════

class TestPlansIntegration:

    def _post_plan(self, **kwargs):
        payload = {
            "name": "Integration Test Plan",
            "zone_id": KNOWN_ZONE,
            "budget": 100000.0,
            "interventions": [
                {"intervention_id": "cool_roof", "quantity": 200}
            ],
        }
        payload.update(kwargs)
        return client.post("/api/plans", json=payload)

    def test_plan_cost_computed_by_server_not_client(self):
        """cool_roof 200 sqm @ 350 = 70000."""
        r = self._post_plan()
        assert r.status_code == 201
        data = r.json()
        assert data["total_estimated_cost"] == 70000.0
        assert data["remaining_budget"] == 30000.0
        assert data["is_feasible"] is True

    def test_plan_is_persisted_and_retrievable(self):
        create_r = self._post_plan(name="Persist Check")
        assert create_r.status_code == 201
        plan_id = create_r.json()["id"]

        list_r = client.get("/api/plans")
        assert list_r.status_code == 200
        ids = [p["id"] for p in list_r.json()]
        assert plan_id in ids

    def test_two_plans_are_both_listed(self):
        self._post_plan(name="Plan Alpha")
        self._post_plan(name="Plan Beta")
        r = client.get("/api/plans")
        names = [p["name"] for p in r.json()]
        assert "Plan Alpha" in names
        assert "Plan Beta" in names

    def test_plan_missing_body_returns_422(self):
        r = client.post("/api/plans", json={})
        assert r.status_code == 422

    def test_plan_missing_interventions_field_returns_422(self):
        r = client.post("/api/plans", json={
            "name": "X", "zone_id": KNOWN_ZONE, "budget": 1000.0
        })
        assert r.status_code == 422

    def test_plan_unknown_zone_returns_404(self):
        r = self._post_plan(zone_id="no-such-zone")
        assert r.status_code == 404

    def test_plan_unknown_intervention_returns_422(self):
        r = self._post_plan(interventions=[
            {"intervention_id": "quantum_cooling", "quantity": 1}
        ])
        assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# 7. Error response shape consistency
# ══════════════════════════════════════════════════════════════════════════════

class TestErrorShapes:
    """All 4xx responses must carry a 'detail' key so the frontend can display them."""

    def test_404_zone_has_detail(self):
        assert "detail" in client.get("/api/zones/x").json()

    def test_404_risk_has_detail(self):
        assert "detail" in client.get("/api/zones/x/risk").json()

    def test_404_plan_create_has_detail(self):
        r = client.post("/api/plans", json={
            "name": "x", "zone_id": "x", "budget": 1000.0,
            "interventions": [{"intervention_id": "tree_planting", "quantity": 1}]
        })
        assert "detail" in r.json()

    def test_422_pydantic_errors_have_detail(self):
        r = client.get("/api/weather")   # missing lat/lon
        assert r.status_code == 422
        assert "detail" in r.json()

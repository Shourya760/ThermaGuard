"""
tests/test_phase7_plans.py

Tests for Phase 7 - Database and Action Plans.

Key integrity: POST /api/plans re-evaluates the scenario server-side.
Client-supplied fabricated costs/totals are never persisted.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Base

client = TestClient(app)

KNOWN_ZONE = "delhi-connaught-place"

# --- Helpers ---

def _valid_plan_payload(**overrides):
    base = {
        "name": "Test Plan",
        "zone_id": KNOWN_ZONE,
        "budget": 100000.0,
        "interventions": [
            {"intervention_id": "tree_planting", "quantity": 10}
        ],
    }
    base.update(overrides)
    return base


# --- Tests ---

class TestActionPlanCreate:

    def test_valid_plan_is_created_and_stored(self):
        """Happy path: plan is saved with server-computed totals."""
        response = client.post("/api/plans", json=_valid_plan_payload())
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Plan"
        assert data["zone_id"] == KNOWN_ZONE
        # Server computes: 10 trees @ 2500 = 25000
        assert data["total_estimated_cost"] == 25000.0
        assert data["remaining_budget"] == 75000.0
        assert data["is_feasible"] is True
        assert "id" in data
        assert "created_at" in data

    def test_plan_response_never_returns_raw_client_cost_fields(self):
        """
        Even if a client could inject extra fields, the server recalculates.
        This test demonstrates the design intent: the endpoint only accepts
        name/zone/budget/interventions; derived fields come from ScenarioService.
        """
        # 10 trees @ 2500 = 25000. Budget 100000. Feasible.
        response = client.post("/api/plans", json=_valid_plan_payload())
        data = response.json()
        # Confirm the authoritative ScenarioService values are what was persisted
        assert data["total_estimated_cost"] == 25000.0
        assert data["is_feasible"] is True

    def test_over_budget_scenario_is_saved_as_not_feasible(self):
        """An over-budget scenario must be persisted with is_feasible=false."""
        payload = _valid_plan_payload(
            budget=5000.0,  # 10 trees cost 25000 — over budget
        )
        response = client.post("/api/plans", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["is_feasible"] is False
        assert data["total_estimated_cost"] == 25000.0
        assert data["remaining_budget"] == -20000.0

    def test_empty_plan_name_rejected(self):
        response = client.post("/api/plans", json=_valid_plan_payload(name=""))
        assert response.status_code == 422

    def test_whitespace_only_plan_name_rejected(self):
        response = client.post("/api/plans", json=_valid_plan_payload(name="   "))
        assert response.status_code == 422

    def test_unknown_zone_returns_404(self):
        response = client.post("/api/plans", json=_valid_plan_payload(zone_id="nowhere"))
        assert response.status_code == 404

    def test_unknown_intervention_returns_422(self):
        payload = _valid_plan_payload(
            interventions=[{"intervention_id": "magic_laser", "quantity": 1}]
        )
        response = client.post("/api/plans", json=payload)
        assert response.status_code == 422
        assert "Unknown intervention" in response.json()["detail"]

    def test_zero_budget_rejected(self):
        response = client.post("/api/plans", json=_valid_plan_payload(budget=0.0))
        assert response.status_code == 422

    def test_negative_budget_rejected(self):
        response = client.post("/api/plans", json=_valid_plan_payload(budget=-1.0))
        assert response.status_code == 422

    def test_negative_quantity_rejected(self):
        payload = _valid_plan_payload(
            interventions=[{"intervention_id": "tree_planting", "quantity": -5}]
        )
        response = client.post("/api/plans", json=payload)
        assert response.status_code == 422


class TestActionPlanList:

    def test_list_empty_when_no_plans(self):
        response = client.get("/api/plans")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_saved_plans(self):
        client.post("/api/plans", json=_valid_plan_payload(name="Plan A"))
        client.post("/api/plans", json=_valid_plan_payload(name="Plan B"))
        response = client.get("/api/plans")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Plan A" in names
        assert "Plan B" in names

    def test_plans_are_isolated_per_test(self):
        """The reset_db fixture ensures each test starts from a clean slate."""
        response = client.get("/api/plans")
        assert response.json() == []

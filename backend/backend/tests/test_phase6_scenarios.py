"""
tests/test_phase6_scenarios.py

Tests for Phase 6 - Intervention and Budget Scenario Engine.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scenario_service import ScenarioService, InvalidInterventionError
from app.schemas.scenario import ScenarioRequest, InterventionRequest
from app.services.zone_service import ZoneNotFoundError

client = TestClient(app)

KNOWN_ZONE = "delhi-connaught-place"


class TestScenarioService:
    service = ScenarioService()
    
    def test_valid_scenario_within_budget(self):
        req = ScenarioRequest(
            zone_id=KNOWN_ZONE,
            budget=50000.0,
            interventions=[
                InterventionRequest(intervention_id="tree_planting", quantity=10),
                InterventionRequest(intervention_id="cool_roof", quantity=20)
            ]
        )
        
        # 10 trees @ 2500 = 25000
        # 20 sqm cool roof @ 350 = 7000
        # Total = 32000
        
        res = self.service.evaluate_scenario(req)
        assert res.zone_id == KNOWN_ZONE
        assert res.budget == 50000.0
        assert res.total_estimated_cost == 32000.0
        assert res.remaining_budget == 18000.0
        assert res.is_feasible is True
        assert len(res.interventions) == 2
        
        tree_res = next(i for i in res.interventions if i.intervention_id == "tree_planting")
        assert tree_res.estimated_cost_inr == 25000.0
        assert tree_res.quantity_requested == 10
        assert tree_res.unit == "per tree"
        
        # Ensure no risk score reduction was returned
        assert not hasattr(res, "risk_score_reduction")

    def test_scenario_exceeds_budget(self):
        req = ScenarioRequest(
            zone_id=KNOWN_ZONE,
            budget=10000.0,
            interventions=[
                InterventionRequest(intervention_id="tree_planting", quantity=10),
            ]
        )
        # Cost is 25000. Budget is 10000.
        res = self.service.evaluate_scenario(req)
        assert res.is_feasible is False
        assert res.total_estimated_cost == 25000.0
        assert res.remaining_budget == -15000.0
        
    def test_invalid_intervention_id_raises(self):
        req = ScenarioRequest(
            zone_id=KNOWN_ZONE,
            budget=10000.0,
            interventions=[
                InterventionRequest(intervention_id="magic_cooling_ray", quantity=1)
            ]
        )
        with pytest.raises(InvalidInterventionError):
            self.service.evaluate_scenario(req)
            
    def test_unknown_zone_id_raises(self):
        req = ScenarioRequest(
            zone_id="does-not-exist",
            budget=10000.0,
            interventions=[
                InterventionRequest(intervention_id="tree_planting", quantity=1)
            ]
        )
        with pytest.raises(ZoneNotFoundError):
            self.service.evaluate_scenario(req)
            

class TestScenarioEndpoint:
    
    def test_post_scenario_success(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 100000.0,
            "interventions": [
                {"intervention_id": "shade_structure", "quantity": 10}
            ]
        }
        # 10 * 4500 = 45000
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_feasible"] is True
        assert data["total_estimated_cost"] == 45000.0
        assert len(data["interventions"]) == 1
        assert "qualitative_benefit" in data["interventions"][0]
        assert "limitations" in data["interventions"][0]
        
    def test_zero_budget_fails_validation(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 0.0,
            "interventions": [
                {"intervention_id": "shade_structure", "quantity": 10}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 422 # Pydantic validation error
        
    def test_negative_budget_fails_validation(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": -50.0,
            "interventions": [
                {"intervention_id": "shade_structure", "quantity": 10}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 422
        
    def test_negative_quantity_fails_validation(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 1000.0,
            "interventions": [
                {"intervention_id": "shade_structure", "quantity": -5}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 422
        
    def test_unknown_intervention_returns_422(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 1000.0,
            "interventions": [
                {"intervention_id": "fake_stuff", "quantity": 5}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 422
        assert "Unknown intervention" in response.json()["detail"]
        
    def test_duplicate_intervention_returns_422(self):
        payload = {
            "zone_id": KNOWN_ZONE,
            "budget": 1000.0,
            "interventions": [
                {"intervention_id": "tree_planting", "quantity": 5},
                {"intervention_id": "tree_planting", "quantity": 10}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 422
        assert "Duplicate intervention_id" in response.json()["detail"][0]["msg"]
        
    def test_unknown_zone_returns_404(self):
        payload = {
            "zone_id": "nowhere",
            "budget": 1000.0,
            "interventions": [
                {"intervention_id": "tree_planting", "quantity": 5}
            ]
        }
        response = client.post("/api/scenarios", json=payload)
        assert response.status_code == 404

"""
tests/test_phase2.py

Automated tests for Phase 2 — configuration and foundation.

What is tested:
1. Settings load with the built-in defaults (no .env file needed).
2. CORS origins default list contains the expected Vite dev ports.
3. CORS origin parsing accepts a comma-separated string (as it would arrive
   from a real environment variable).
4. GET / still returns the expected welcome message.
5. GET /api/health returns status "ok" and exposes the active environment name.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

client = TestClient(app)


# ─── Configuration tests ───────────────────────────────────────────────────────

def test_default_app_env():
    """Settings should default to 'development' when no env var is set."""
    s = Settings()
    assert s.app_env == "development"


def test_default_cors_origins_contain_vite_ports():
    """Default CORS list must include the two expected Vite dev-server origins."""
    s = Settings()
    assert "http://localhost:5173" in s.cors_origins
    assert "http://localhost:5174" in s.cors_origins


def test_cors_origins_parsed_from_comma_string():
    """
    When CORS_ORIGINS arrives as a comma-separated env-var string the validator
    must split and strip it into a proper list.
    """
    s = Settings(cors_origins="http://localhost:3000, http://localhost:4000")
    assert s.cors_origins == ["http://localhost:3000", "http://localhost:4000"]


def test_cors_origins_list_passed_directly():
    """When a list is supplied directly (test overrides) it should be accepted as-is."""
    s = Settings(cors_origins=["http://example.com"])
    assert s.cors_origins == ["http://example.com"]


# ─── Endpoint smoke tests ──────────────────────────────────────────────────────

def test_root_endpoint():
    """GET / must return 200 and the welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to CoolBlock API"}


def test_health_endpoint_status():
    """GET /api/health must return 200 and status 'ok'."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_endpoint_exposes_env():
    """GET /api/health must include the 'env' field from settings."""
    response = client.get("/api/health")
    assert "env" in response.json()

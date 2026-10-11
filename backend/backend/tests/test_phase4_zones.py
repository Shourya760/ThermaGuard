"""
tests/test_phase4_zones.py

Automated tests for Phase 4 — Zone Data and Zone APIs.

No internet access is required. All tests operate against the in-memory
zone dataset loaded from app/data/demo_zones.json.

Test categories:
  A. ZoneService unit tests
       - list_zones returns the expected number of zones
       - get_zone returns a ZoneDetail with correct fields
       - get_zone raises ZoneNotFoundError for unknown IDs

  B. GET /api/zones endpoint tests
       - returns 200 with a list
       - every item has required ZoneSummary fields
       - data_status is present and equals 'DEMO' for all current zones

  C. GET /api/zones/{zone_id} endpoint tests
       - known ID returns 200 and full ZoneDetail
       - unknown ID returns 404 with helpful message
       - response includes provenance fields
       - response includes heat_indicators block with null fields
       - response does NOT contain fabricated numeric indicator values

  D. Data integrity tests
       - all zones have valid latitude/longitude ranges
       - all zones have coordinate_source and data_provenance fields
       - heat_indicators missing_data_reason is non-empty for null fields
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.zone_service import ZoneService, ZoneNotFoundError

client = TestClient(app)

# A real zone ID that must exist in the dataset
KNOWN_ZONE_ID = "delhi-connaught-place"
UNKNOWN_ZONE_ID = "zone-that-does-not-exist-xyz"


# ===========================================================================
# A. ZoneService unit tests
# ===========================================================================

class TestZoneService:

    service = ZoneService()

    def test_list_zones_returns_multiple_zones(self):
        zones = self.service.list_zones()
        assert len(zones) >= 2, "Expected at least 2 zones in the pilot dataset."

    def test_list_zones_all_have_required_fields(self):
        for zone in self.service.list_zones():
            assert zone.id
            assert zone.name
            assert zone.city
            assert zone.country
            assert zone.area_type
            assert zone.data_status in ("DEMO", "VERIFIED")

    def test_get_known_zone_returns_zone_detail(self):
        zone = self.service.get_zone(KNOWN_ZONE_ID)
        assert zone.id == KNOWN_ZONE_ID
        assert zone.name  # non-empty
        assert zone.latitude is not None
        assert zone.longitude is not None

    def test_get_zone_includes_provenance(self):
        zone = self.service.get_zone(KNOWN_ZONE_ID)
        assert zone.coordinate_source
        assert zone.data_provenance

    def test_get_zone_includes_heat_indicators_block(self):
        zone = self.service.get_zone(KNOWN_ZONE_ID)
        assert zone.heat_indicators is not None

    def test_get_unknown_zone_raises_zone_not_found(self):
        with pytest.raises(ZoneNotFoundError) as exc_info:
            self.service.get_zone(UNKNOWN_ZONE_ID)
        assert UNKNOWN_ZONE_ID in str(exc_info.value)

    def test_list_zones_is_ordered_consistently(self):
        """list_zones should return zones in a stable, predictable order."""
        first_call = [z.id for z in self.service.list_zones()]
        second_call = [z.id for z in self.service.list_zones()]
        assert first_call == second_call


# ===========================================================================
# B. GET /api/zones endpoint tests
# ===========================================================================

class TestListZonesEndpoint:

    def test_list_zones_returns_200(self):
        response = client.get("/api/zones")
        assert response.status_code == 200

    def test_list_zones_returns_a_list(self):
        response = client.get("/api/zones")
        assert isinstance(response.json(), list)

    def test_list_zones_contains_at_least_two_zones(self):
        response = client.get("/api/zones")
        assert len(response.json()) >= 2

    def test_list_zones_items_have_required_fields(self):
        response = client.get("/api/zones")
        for item in response.json():
            assert "id" in item
            assert "name" in item
            assert "city" in item
            assert "country" in item
            assert "latitude" in item
            assert "longitude" in item
            assert "area_type" in item
            assert "data_status" in item

    def test_list_zones_all_current_zones_are_demo(self):
        """All zones in the MVP dataset must be labelled DEMO."""
        response = client.get("/api/zones")
        for item in response.json():
            assert item["data_status"] == "DEMO", (
                f"Zone '{item['id']}' has data_status='{item['data_status']}' "
                f"but expected 'DEMO' for the hackathon MVP dataset."
            )

    def test_list_zones_does_not_include_heat_indicators(self):
        """
        The list endpoint returns ZoneSummary (compact).
        It must NOT include the heat_indicators block to keep responses small.
        """
        response = client.get("/api/zones")
        for item in response.json():
            assert "heat_indicators" not in item, (
                f"Zone '{item['id']}' unexpectedly includes heat_indicators "
                f"in the list response (should only appear in detail endpoint)."
            )


# ===========================================================================
# C. GET /api/zones/{zone_id} endpoint tests
# ===========================================================================

class TestGetZoneEndpoint:

    def test_known_zone_id_returns_200(self):
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        assert response.status_code == 200

    def test_unknown_zone_id_returns_404(self):
        response = client.get(f"/api/zones/{UNKNOWN_ZONE_ID}")
        assert response.status_code == 404

    def test_404_response_includes_helpful_message(self):
        response = client.get(f"/api/zones/{UNKNOWN_ZONE_ID}")
        detail = response.json().get("detail", "")
        assert UNKNOWN_ZONE_ID in detail or "not found" in detail.lower()

    def test_zone_detail_has_all_required_fields(self):
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        data = response.json()
        required = [
            "id", "name", "city", "country",
            "latitude", "longitude", "area_type",
            "description", "coordinate_source", "data_provenance",
            "data_status", "heat_indicators",
        ]
        for field in required:
            assert field in data, f"Missing required field: '{field}'"

    def test_zone_detail_id_matches_requested_id(self):
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        assert response.json()["id"] == KNOWN_ZONE_ID

    def test_zone_detail_data_status_is_demo(self):
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        assert response.json()["data_status"] == "DEMO"

    def test_zone_detail_heat_indicators_are_null(self):
        """
        For DEMO zones the numeric heat-indicator fields must be null,
        never a fabricated value.
        """
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        indicators = response.json()["heat_indicators"]
        assert indicators["land_surface_temperature_celsius"] is None
        assert indicators["vegetation_coverage_percent"] is None
        assert indicators["shade_coverage_percent"] is None
        assert indicators["population_vulnerability_index"] is None

    def test_zone_detail_missing_data_reason_is_present(self):
        """If indicators are null, missing_data_reason must explain why."""
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        indicators = response.json()["heat_indicators"]
        reason = indicators.get("missing_data_reason")
        assert reason, "missing_data_reason should be non-empty when indicators are null."

    def test_zone_detail_provenance_fields_are_non_empty(self):
        response = client.get(f"/api/zones/{KNOWN_ZONE_ID}")
        data = response.json()
        assert data["coordinate_source"].strip()
        assert data["data_provenance"].strip()


# ===========================================================================
# D. Data integrity tests (run against the full dataset)
# ===========================================================================

class TestZoneDataIntegrity:
    """
    These tests enforce data-quality rules across every zone in the dataset.
    They fail fast if someone adds a zone with invented indicator values or
    invalid coordinates.
    """

    service = ZoneService()

    def _all_zone_details(self):
        return [self.service.get_zone(z.id) for z in self.service.list_zones()]

    def test_all_latitudes_in_valid_range(self):
        for zone in self._all_zone_details():
            assert -90.0 <= zone.latitude <= 90.0, (
                f"Zone '{zone.id}' has invalid latitude: {zone.latitude}"
            )

    def test_all_longitudes_in_valid_range(self):
        for zone in self._all_zone_details():
            assert -180.0 <= zone.longitude <= 180.0, (
                f"Zone '{zone.id}' has invalid longitude: {zone.longitude}"
            )

    def test_all_zones_have_coordinate_source(self):
        for zone in self._all_zone_details():
            assert zone.coordinate_source.strip(), (
                f"Zone '{zone.id}' is missing coordinate_source."
            )

    def test_all_zones_have_data_provenance(self):
        for zone in self._all_zone_details():
            assert zone.data_provenance.strip(), (
                f"Zone '{zone.id}' is missing data_provenance."
            )

    def test_no_zone_has_fabricated_lst(self):
        """
        land_surface_temperature_celsius must be null for all DEMO zones.
        This prevents someone accidentally adding a made-up LST value.
        """
        for zone in self._all_zone_details():
            if zone.data_status == "DEMO":
                assert zone.heat_indicators.land_surface_temperature_celsius is None, (
                    f"Zone '{zone.id}' is DEMO but has a non-null LST value. "
                    f"Only verified satellite data should populate this field."
                )

    def test_no_zone_has_fabricated_vegetation(self):
        for zone in self._all_zone_details():
            if zone.data_status == "DEMO":
                assert zone.heat_indicators.vegetation_coverage_percent is None, (
                    f"Zone '{zone.id}' is DEMO but has a non-null vegetation value."
                )

    def test_all_zone_ids_are_unique(self):
        ids = [z.id for z in self.service.list_zones()]
        assert len(ids) == len(set(ids)), "Duplicate zone IDs found in the dataset."

    def test_all_zone_ids_are_slug_formatted(self):
        """Zone IDs must be lowercase slugs (letters, digits, hyphens only)."""
        import re
        slug_pattern = re.compile(r'^[a-z0-9-]+$')
        for zone in self.service.list_zones():
            assert slug_pattern.match(zone.id), (
                f"Zone ID '{zone.id}' is not a valid lowercase slug."
            )

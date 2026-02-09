"""
Phase A: Contract Compatibility Ratchet.

Ensures the GuardianResult schema cannot drift without a version bump.
Snapshots the frozen key structure and asserts compatibility on every run.

Tests:
1. Top-level keys match CONTRACT_SCHEMA_SNAPSHOT
2. Check-level keys match CHECK_SCHEMA_KEYS
3. Artifact-level keys match ARTIFACT_SCHEMA_KEYS
4. check_schema_compatibility catches extra keys
5. check_schema_compatibility catches missing keys
6. Version bump required on key change (migration test)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.types.guardian_contract import (
    ARTIFACT_SCHEMA_KEYS,
    ARTIFACT_TYPE_VALUES,
    CHECK_SCHEMA_KEYS,
    CHECK_STATUS_VALUES,
    CONTRACT_SCHEMA_SNAPSHOT,
    CONTRACT_VERSION,
    GUARDIAN_STATUS_VALUES,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    validate_against_json_schema,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# 1. Snapshot fidelity — top-level keys
# ---------------------------------------------------------------------------


class TestSchemaSnapshot:
    """The serialized shape of GuardianResult must match the frozen snapshot."""

    EXPECTED_REQUIRED_KEYS = {
        "guardian_id",
        "version",
        "status",
        "summary",
        "checks",
        "artifacts",
        "metrics",
        "remediation_hints",
    }
    EXPECTED_OPTIONAL_KEYS = {"timestamp", "correlation_id"}

    def test_snapshot_has_all_required_keys(self):
        assert self.EXPECTED_REQUIRED_KEYS.issubset(CONTRACT_SCHEMA_SNAPSHOT.keys())

    def test_snapshot_has_optional_keys(self):
        assert self.EXPECTED_OPTIONAL_KEYS.issubset(CONTRACT_SCHEMA_SNAPSHOT.keys())

    def test_snapshot_has_no_extra_keys(self):
        all_expected = self.EXPECTED_REQUIRED_KEYS | self.EXPECTED_OPTIONAL_KEYS
        assert set(CONTRACT_SCHEMA_SNAPSHOT.keys()) == all_expected

    def test_result_serialization_matches_snapshot(self):
        r = GuardianResult(guardian_id="compat_test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        r.add_artifact(ArtifactType.JSON, "foo/bar.json", "test")
        d = r.to_dict()
        errors = check_schema_compatibility(d)
        assert errors == [], f"Schema drift: {errors}"

    def test_result_with_optionals_matches(self):
        r = GuardianResult(
            guardian_id="compat_test",
            timestamp="2026-01-01T00:00:00Z",
            correlation_id="abc-123",
        )
        d = r.to_dict()
        errors = check_schema_compatibility(d)
        assert errors == [], f"Schema drift with optionals: {errors}"


# ---------------------------------------------------------------------------
# 2. Check-level key snapshot
# ---------------------------------------------------------------------------


class TestCheckKeySnapshot:
    def test_check_keys_frozen(self):
        assert CHECK_SCHEMA_KEYS == {"check_id", "status", "details", "evidence"}

    def test_check_serialization_matches(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok", evidence={"x": 1})
        check_dict = r.to_dict()["checks"][0]
        assert set(check_dict.keys()) == CHECK_SCHEMA_KEYS


# ---------------------------------------------------------------------------
# 3. Artifact-level key snapshot
# ---------------------------------------------------------------------------


class TestArtifactKeySnapshot:
    def test_artifact_keys_frozen(self):
        assert ARTIFACT_SCHEMA_KEYS == {"type", "path", "description"}

    def test_artifact_serialization_matches(self):
        r = GuardianResult(guardian_id="test")
        r.add_artifact(ArtifactType.JSON, "foo.json", "desc")
        artifact_dict = r.to_dict()["artifacts"][0]
        assert set(artifact_dict.keys()) == ARTIFACT_SCHEMA_KEYS


# ---------------------------------------------------------------------------
# 4. Compatibility gate catches drift
# ---------------------------------------------------------------------------


class TestCompatibilityGate:
    def test_extra_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["rogue_key"] = "bad"
        errors = check_schema_compatibility(d)
        assert any("rogue_key" in e for e in errors)

    def test_missing_required_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        del d["metrics"]
        errors = check_schema_compatibility(d)
        assert any("metrics" in e for e in errors)

    def test_extra_check_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [{"check_id": "c1", "status": "PASS", "details": "ok", "evidence": {}, "extra": True}]
        errors = check_schema_compatibility(d)
        assert any("Check keys mismatch" in e for e in errors)

    def test_clean_result_passes_gate(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        errors = check_schema_compatibility(r.to_dict())
        assert errors == []


# ---------------------------------------------------------------------------
# 5. Version bump migration test
# ---------------------------------------------------------------------------


class TestVersionBump:
    def test_contract_version_is_integer(self):
        assert isinstance(CONTRACT_VERSION, int)
        assert CONTRACT_VERSION >= 1

    def test_version_in_result_matches_contract(self):
        r = GuardianResult(guardian_id="test")
        assert r.version == CONTRACT_VERSION

    def test_snapshot_key_count_is_locked(self):
        """If this fails, CONTRACT_VERSION must be bumped."""
        assert len(CONTRACT_SCHEMA_SNAPSHOT) == 10, (
            f"Schema key count changed from 10 to {len(CONTRACT_SCHEMA_SNAPSHOT)}. "
            f"Bump CONTRACT_VERSION from {CONTRACT_VERSION}."
        )


# ---------------------------------------------------------------------------
# 6. JSON Schema validation (Phase 2: Schema-level compatibility)
# ---------------------------------------------------------------------------


class TestJsonSchemaValidation:
    """Validate results against the full JSON Schema snapshot."""

    def test_valid_result_passes_schema(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        r.add_artifact(ArtifactType.JSON, "foo.json", "desc")
        errors = validate_against_json_schema(r.to_dict())
        assert errors == [], f"Schema validation errors: {errors}"

    def test_invalid_status_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["status"] = "INVALID_STATUS"
        errors = validate_against_json_schema(d)
        assert any("enum" in e and "INVALID_STATUS" in e for e in errors)

    def test_invalid_check_status_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [{"check_id": "c1", "status": "BADSTATUS", "details": "ok", "evidence": {}}]
        errors = validate_against_json_schema(d)
        assert any("enum" in e for e in errors)

    def test_invalid_artifact_type_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [{"type": "badtype", "path": "foo.json", "description": "desc"}]
        errors = validate_against_json_schema(d)
        assert any("enum" in e for e in errors)

    def test_missing_required_field_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        del d["summary"]
        errors = validate_against_json_schema(d)
        assert any("summary" in e for e in errors)

    def test_extra_field_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["extra_field"] = "should not be here"
        errors = validate_against_json_schema(d)
        assert any("extra_field" in e for e in errors)


# ---------------------------------------------------------------------------
# 7. Enum value locking (Phase 2)
# ---------------------------------------------------------------------------


class TestEnumValueLocking:
    """Enum values are frozen; any change requires version bump."""

    def test_guardian_status_values_locked(self):
        assert GUARDIAN_STATUS_VALUES == {"PASS", "FAIL", "ERROR"}

    def test_check_status_values_locked(self):
        assert CHECK_STATUS_VALUES == {"PASS", "FAIL", "SKIP"}

    def test_artifact_type_values_locked(self):
        assert ARTIFACT_TYPE_VALUES == {"diff", "json", "log", "snapshot"}

    def test_enum_matches_frozen_values(self):
        assert set(s.value for s in GuardianStatus) == GUARDIAN_STATUS_VALUES
        assert set(s.value for s in CheckStatus) == CHECK_STATUS_VALUES
        assert set(t.value for t in ArtifactType) == ARTIFACT_TYPE_VALUES


# ---------------------------------------------------------------------------
# 8. Synthetic breaking change test (Phase 2)
# ---------------------------------------------------------------------------


class TestSyntheticBreakingChange:
    """Demonstrate that schema violations are caught before version bump."""

    def test_new_required_field_fails_without_version_bump(self):
        """A result with a missing field fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        del d["remediation_hints"]
        errors = validate_against_json_schema(d)
        assert len(errors) > 0, "Missing required field should fail"

    def test_new_enum_value_fails_validation(self):
        """A result with an invalid enum value fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["status"] = "WARNING"  # New value not in schema
        errors = validate_against_json_schema(d)
        assert any("WARNING" in e for e in errors), "New enum value should fail"

    def test_type_change_fails_validation(self):
        """A result with wrong type fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["version"] = "1"  # String instead of int
        errors = validate_against_json_schema(d)
        assert any("integer" in e or "version" in e for e in errors)

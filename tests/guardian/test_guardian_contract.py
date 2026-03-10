"""
Guardian Contract Tests — Schema, Status Promotion, and Contract Integrity.

Verifies:
1. Status promotion: FAIL check promotes top-level status to FAIL
2. Status promotion: ERROR status is sticky (not overwritten by FAIL)
3. Schema compliance across all contract fields
4. Serialization round-trip determinism
5. Artifact path normalization (no absolute paths, no backslashes)
6. Contract version is pinned
7. check_schema_compatibility detects missing/extra keys
8. validate_against_json_schema detects type and enum violations
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.types.guardian_contract_types import (
    CONTRACT_VERSION,
    ArtifactClass,
    ArtifactType,
    CheckStatus,
    GuardianCheck,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    normalize_repo_path,
    validate_against_json_schema,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(guardian_id: str = "test_guardian") -> GuardianResult:
    return GuardianResult(guardian_id=guardian_id)


# ---------------------------------------------------------------------------
# 1. Status promotion: FAIL check → top-level FAIL
# ---------------------------------------------------------------------------


class TestStatusPromotion:
    """Verify that a FAIL check correctly promotes the top-level status."""

    def test_initial_status_is_pass(self):
        result = _make_result()
        assert result.status == GuardianStatus.PASS.value

    def test_single_fail_check_promotes_to_fail(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "something failed")
        assert result.status == GuardianStatus.FAIL.value

    def test_pass_check_does_not_change_pass_status(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        assert result.status == GuardianStatus.PASS.value

    def test_skip_check_does_not_change_pass_status(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.SKIP, "not applicable")
        assert result.status == GuardianStatus.PASS.value

    def test_fail_after_pass_promotes_to_fail(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        result.add_check("c2", CheckStatus.FAIL, "bad")
        assert result.status == GuardianStatus.FAIL.value

    def test_pass_after_fail_does_not_revert_to_pass(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "bad")
        result.add_check("c2", CheckStatus.PASS, "ok later")
        assert result.status == GuardianStatus.FAIL.value

    def test_error_status_is_sticky_over_fail(self):
        result = _make_result()
        result.set_error("scan crashed")
        result.add_check("c1", CheckStatus.FAIL, "also failed")
        assert result.status == GuardianStatus.ERROR.value

    def test_multiple_fail_checks_status_still_fail(self):
        result = _make_result()
        for i in range(5):
            result.add_check(f"c{i}", CheckStatus.FAIL, f"fail {i}")
        assert result.status == GuardianStatus.FAIL.value

    def test_string_fail_value_also_promotes(self):
        result = _make_result()
        result.add_check("c1", "FAIL", "string-based FAIL")
        assert result.status == GuardianStatus.FAIL.value

    def test_status_promotion_boundary_single_check(self):
        result = _make_result()
        result.add_check("only_check", CheckStatus.FAIL, "the only check failed")
        assert result.status == GuardianStatus.FAIL.value
        assert len(result.checks) == 1


# ---------------------------------------------------------------------------
# 2. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths_on_clean_result(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == []

    def test_check_schema_compatibility_clean(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        errors = check_schema_compatibility(result.to_dict())
        assert errors == []

    def test_contract_version_is_pinned(self):
        result = _make_result()
        assert result.version == CONTRACT_VERSION

    def test_guardian_id_is_required(self):
        result = GuardianResult(guardian_id="my_guardian")
        assert result.guardian_id == "my_guardian"
        d = result.to_dict()
        assert d["guardian_id"] == "my_guardian"

    def test_status_values_are_valid_enum(self):
        for gid, status_str in [("a", "PASS"), ("b", "FAIL"), ("c", "ERROR")]:
            result = GuardianResult(guardian_id=gid, status=status_str)
            errors = check_schema_compatibility(result.to_dict())
            assert errors == [], f"Unexpected schema errors for status={status_str}: {errors}"

    def test_check_schema_keys_exact(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok", evidence={"key": "val"})
        d = result.to_dict()
        for check in d["checks"]:
            assert set(check.keys()) == {"check_id", "status", "details", "evidence"}

    def test_artifact_schema_keys_exact(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "docs/out.json", "output")
        d = result.to_dict()
        for artifact in d["artifacts"]:
            assert set(artifact.keys()) == {"type", "path", "description"}

    def test_validate_against_json_schema_clean(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        errors = validate_against_json_schema(result.to_dict())
        assert errors == [], f"JSON schema errors: {errors}"

    def test_validate_against_json_schema_invalid_status_caught(self):
        result = _make_result()
        d = result.to_dict()
        d["status"] = "UNKNOWN_STATUS"
        errors = validate_against_json_schema(d)
        assert any("status" in e for e in errors), f"Expected status error, got: {errors}"

    def test_missing_required_key_detected(self):
        result = _make_result()
        d = result.to_dict()
        del d["guardian_id"]
        errors = validate_against_json_schema(d)
        assert any("guardian_id" in e for e in errors)

    def test_extra_key_detected_by_schema_compatibility(self):
        result = _make_result()
        d = result.to_dict()
        d["rogue_key"] = "value"
        errors = check_schema_compatibility(d)
        assert any("rogue_key" in e for e in errors)


# ---------------------------------------------------------------------------
# 3. Artifact path normalization
# ---------------------------------------------------------------------------


class TestArtifactPathNormalization:
    def test_backslash_normalized_to_forward(self):
        normalized = normalize_repo_path("docs\\reports\\out.json")
        assert "\\" not in normalized
        assert "/" in normalized

    def test_no_leading_slash(self):
        normalized = normalize_repo_path("/docs/reports/out.json")
        assert not normalized.startswith("/")

    def test_windows_drive_stripped(self):
        normalized = normalize_repo_path("C:/docs/reports/out.json")
        assert not normalized.startswith("C:")
        assert not normalized.startswith("/")

    def test_dot_segment_collapsed(self):
        normalized = normalize_repo_path("docs/./reports/out.json")
        assert "/." not in normalized

    def test_dotdot_raises(self):
        with pytest.raises(ValueError, match=r"\.\."):
            normalize_repo_path("docs/../etc/passwd")

    def test_artifact_path_in_result_is_normalized(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "docs/reports/out.json", "output")
        d = result.to_dict()
        paths = [a["path"] for a in d["artifacts"]]
        assert all("\\" not in p for p in paths)
        assert all(not p.startswith("/") for p in paths)


# ---------------------------------------------------------------------------
# 4. Serialization round-trip determinism
# ---------------------------------------------------------------------------


class TestSerializationDeterminism:
    def test_same_result_same_dict_twice(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        d1 = result.to_dict()
        d2 = result.to_dict()
        assert d1 == d2

    def test_sorted_checks_in_output(self):
        result = _make_result()
        result.add_check("z_check", CheckStatus.PASS, "last alphabetically")
        result.add_check("a_check", CheckStatus.FAIL, "first alphabetically")
        d = result.to_dict()
        ids = [c["check_id"] for c in d["checks"]]
        assert ids == sorted(ids), f"checks not sorted: {ids}"

    def test_sorted_remediation_hints(self):
        result = _make_result()
        result.remediation_hints = ["z_hint", "a_hint", "m_hint"]
        d = result.to_dict()
        hints = d["remediation_hints"]
        assert hints == sorted(hints)

    def test_sorted_artifacts_in_output(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "z_path/out.json", "z artifact")
        result.add_artifact(ArtifactType.JSON, "a_path/out.json", "a artifact")
        d = result.to_dict()
        paths = [a["path"] for a in d["artifacts"]]
        assert paths == sorted(paths)

    def test_metrics_sorted_by_key(self):
        result = _make_result()
        result.metrics = {"z_count": 5, "a_count": 1, "m_count": 3}
        d = result.to_dict()
        keys = list(d["metrics"].keys())
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# 5. Malformed / hostile inputs
# ---------------------------------------------------------------------------


class TestMalformedInputs:
    def test_empty_guardian_id_captured_in_validate(self):
        result = GuardianResult(guardian_id="")
        errors = result.validate()
        assert any("guardian_id" in e for e in errors)

    def test_invalid_check_status_caught_in_validate(self):
        result = GuardianResult(guardian_id="test")
        result.checks.append(GuardianCheck(check_id="c1", status="BOGUS", details="bad", evidence={}))
        errors = result.validate()
        assert any("status" in e for e in errors)

    def test_absolute_path_in_evidence_caught(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "fail", evidence={"path": "/etc/passwd"})
        violations = validate_no_absolute_paths(result.to_dict())
        assert len(violations) > 0

    def test_windows_absolute_path_in_evidence_caught(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "fail", evidence={"path": "C:\\Windows\\system32"})
        violations = validate_no_absolute_paths(result.to_dict())
        assert len(violations) > 0

    def test_none_timestamp_not_in_dict(self):
        result = _make_result()
        assert result.timestamp is None
        d = result.to_dict()
        assert "timestamp" not in d or d.get("timestamp") is None

    def test_artifact_class_defaults_to_individual(self):
        result = _make_result()
        assert result.artifact_class == ArtifactClass.INDIVIDUAL.value

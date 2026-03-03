"""
Guardian Contract Schema Tests — ReAct-Style.

Observe → Verify → Report pattern for the canonical GuardianResult schema.

Tests:
1. Schema validity (all required fields present, correct types)
2. Path normalization (no absolute paths, POSIX only)
3. Status promotion logic (FAIL check → FAIL result)
4. Serialization round-trip (to_json → load → identical)
5. Validation catches invalid data
6. Artifact paths are always repo-relative POSIX
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.types.guardian_contract_types import (
    CONTRACT_VERSION,
    ArtifactType,
    CheckStatus,
    GuardianArtifact,
    GuardianCheck,
    GuardianResult,
    GuardianStatus,
    load_guardian_result,
    normalize_repo_path,
    validate_no_absolute_paths,
    write_guardian_result,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def passing_result() -> GuardianResult:
    """A minimal passing GuardianResult."""
    r = GuardianResult(guardian_id="test_guardian")
    r.add_check("check_a", CheckStatus.PASS, "All good")
    r.metrics["items_scanned"] = 42
    return r


@pytest.fixture
def failing_result() -> GuardianResult:
    """A GuardianResult with one failing check."""
    r = GuardianResult(guardian_id="test_guardian")
    r.add_check("check_a", CheckStatus.PASS, "Fine")
    r.add_check("check_b", CheckStatus.FAIL, "Bad thing", evidence={"count": 3})
    r.remediation_hints = ["Fix the bad thing"]
    return r


@pytest.fixture
def error_result() -> GuardianResult:
    """A GuardianResult in ERROR state."""
    r = GuardianResult(guardian_id="test_guardian")
    r.set_error("Unexpected crash in scan")
    return r


# ---------------------------------------------------------------------------
# 1. Schema validity
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify GuardianResult has all required contract fields."""

    def test_required_fields_present(self, passing_result: GuardianResult):
        d = passing_result.to_dict()
        required = {
            "guardian_id",
            "version",
            "status",
            "summary",
            "checks",
            "artifacts",
            "metrics",
            "remediation_hints",
        }
        assert required.issubset(d.keys()), f"Missing keys: {required - d.keys()}"

    def test_version_matches_contract(self, passing_result: GuardianResult):
        assert passing_result.version == CONTRACT_VERSION

    def test_checks_have_required_fields(self, passing_result: GuardianResult):
        for check in passing_result.to_dict()["checks"]:
            assert "check_id" in check
            assert "status" in check
            assert "details" in check
            assert "evidence" in check

    def test_status_enum_values(self):
        assert {s.value for s in GuardianStatus} == {"PASS", "FAIL", "ERROR"}
        assert {s.value for s in CheckStatus} == {"PASS", "FAIL", "SKIP"}


# ---------------------------------------------------------------------------
# 2. Path normalization
# ---------------------------------------------------------------------------


class TestPathNormalization:
    """Verify path normalization produces canonical POSIX paths."""

    @pytest.mark.parametrize(
        "input_path,expected",
        [
            ("agentic_core/L0_routing/scripts/foo.py", "agentic_core/L0_routing/scripts/foo.py"),
            ("agentic_core\\L0_routing\\scripts\\foo.py", "agentic_core/L0_routing/scripts/foo.py"),
            ("./agentic_core/foo.py", "agentic_core/foo.py"),
        ],
    )
    def test_normalize_valid_paths(self, input_path: str, expected: str):
        assert normalize_repo_path(input_path) == expected

    def test_normalize_rejects_dotdot(self):
        with pytest.raises(ValueError, match="\\.\\."):
            normalize_repo_path("agentic_core/../secrets/key.pem")

    def test_artifact_auto_normalizes(self):
        a = GuardianArtifact(
            type=ArtifactType.JSON.value,
            path="agentic_core\\L0_routing\\logs\\result.json",
            description="test",
        )
        assert "\\" not in a.path
        assert a.path == "agentic_core/L0_routing/logs/result.json"

    def test_no_absolute_paths_in_result(self, passing_result: GuardianResult):
        violations = validate_no_absolute_paths(passing_result.to_dict())
        assert violations == [], f"Absolute paths found: {violations}"


# ---------------------------------------------------------------------------
# 3. Status promotion logic
# ---------------------------------------------------------------------------


class TestStatusPromotion:
    """Verify that check failures promote the top-level status correctly."""

    def test_all_pass_stays_pass(self, passing_result: GuardianResult):
        assert passing_result.status == GuardianStatus.PASS.value

    def test_one_fail_promotes_to_fail(self, failing_result: GuardianResult):
        assert failing_result.status == GuardianStatus.FAIL.value

    def test_error_overrides_fail(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.FAIL, "bad")
        r.set_error("crash")
        assert r.status == GuardianStatus.ERROR.value

    def test_skip_does_not_promote(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        r.add_check("c2", CheckStatus.SKIP, "n/a")
        assert r.status == GuardianStatus.PASS.value


# ---------------------------------------------------------------------------
# 4. Serialization round-trip
# ---------------------------------------------------------------------------


class TestSerializationRoundTrip:
    """Verify to_json → load_guardian_result produces identical data."""

    def test_round_trip_passing(self, passing_result: GuardianResult, tmp_path: Path):
        out = write_guardian_result(passing_result, tmp_path)
        loaded = load_guardian_result(out)
        assert loaded.guardian_id == passing_result.guardian_id
        assert loaded.status == passing_result.status
        assert len(loaded.checks) == len(passing_result.checks)
        assert loaded.metrics == passing_result.metrics

    def test_round_trip_failing(self, failing_result: GuardianResult, tmp_path: Path):
        out = write_guardian_result(failing_result, tmp_path)
        loaded = load_guardian_result(out)
        assert loaded.status == GuardianStatus.FAIL.value
        assert loaded.remediation_hints == ["Fix the bad thing"]
        assert len(loaded.checks) == 2

    def test_json_is_valid_json(self, passing_result: GuardianResult):
        raw = passing_result.to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)
        assert parsed["guardian_id"] == "test_guardian"

    def test_timestamp_omitted_when_none(self, passing_result: GuardianResult):
        d = passing_result.to_dict()
        assert "timestamp" not in d

    def test_timestamp_present_when_set(self):
        r = GuardianResult(guardian_id="test", timestamp="2026-01-01T00:00:00Z")
        d = r.to_dict()
        assert d["timestamp"] == "2026-01-01T00:00:00Z"

    def test_deterministic_output(self, passing_result: GuardianResult):
        j1 = passing_result.to_json()
        j2 = passing_result.to_json()
        assert j1 == j2, "Same input must produce identical JSON"


# ---------------------------------------------------------------------------
# 5. Validation catches invalid data
# ---------------------------------------------------------------------------


class TestValidation:
    """Verify GuardianResult.validate() catches contract violations."""

    def test_valid_result_has_no_errors(self, passing_result: GuardianResult):
        assert passing_result.validate() == []

    def test_missing_guardian_id(self):
        r = GuardianResult(guardian_id="")
        errors = r.validate()
        assert any("guardian_id" in e for e in errors)

    def test_invalid_status(self):
        r = GuardianResult(guardian_id="test", status="MAYBE")
        errors = r.validate()
        assert any("Invalid status" in e for e in errors)

    def test_invalid_check_status(self):
        r = GuardianResult(guardian_id="test")
        r.checks.append(GuardianCheck(check_id="c1", status="WARN", details="hmm"))
        errors = r.validate()
        assert any("checks[0].status" in e for e in errors)

    def test_empty_check_id(self):
        r = GuardianResult(guardian_id="test")
        r.checks.append(GuardianCheck(check_id="", status="PASS", details="ok"))
        errors = r.validate()
        assert any("check_id" in e for e in errors)

    def test_invalid_artifact_type(self):
        r = GuardianResult(guardian_id="test")
        r.artifacts.append(GuardianArtifact(type="video", path="foo.mp4", description="nope"))
        errors = r.validate()
        assert any("artifacts[0].type" in e for e in errors)

"""
Contract tests for the L2 HealResult contract.

Proves:
1. validate() passes for minimal valid objects.
2. check_schema_compatibility() passes.
3. Deterministic sorting: unsorted inputs produce sorted outputs in to_dict().
4. Negative tests: invalid status, absolute paths, empty fields rejected.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.L2_execution.types.heal_contract_types import (
    CombinedHealResult,
    HealCheckResult,
    HealStatus,
    check_schema_compatibility,
    validate_against_json_schema,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TIMESTAMP = "2026-02-11T15:00:00Z"


def _minimal_check(check_id: str = "test_check", status: HealStatus = HealStatus.HEALED) -> HealCheckResult:
    return HealCheckResult(check_id=check_id, status=status)


def _minimal_result(**overrides: object) -> CombinedHealResult:
    defaults: dict = {
        "tool_id": "remediation_dispatcher",
        "plan_name": "LEGACY_MIRROR_PLAN",
        "results": (_minimal_check(),),
        "approved_by": ("token_a",),
        "created_utc": TIMESTAMP,
    }
    defaults.update(overrides)
    return CombinedHealResult(**defaults)


# ---------------------------------------------------------------------------
# Positive: validation passes
# ---------------------------------------------------------------------------


class TestHealContractValidation:
    def test_validate_minimal(self) -> None:
        result = _minimal_result()
        assert result.validate() == []

    def test_validate_multiple_checks(self) -> None:
        result = _minimal_result(
            results=(
                _minimal_check("alpha", HealStatus.HEALED),
                _minimal_check("beta", HealStatus.PARTIAL),
                _minimal_check("gamma", HealStatus.FAILED),
                _minimal_check("delta", HealStatus.SKIPPED),
            ),
        )
        assert result.validate() == []

    def test_schema_compatibility_minimal(self) -> None:
        result = _minimal_result()
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_schema_compatibility_with_changes(self) -> None:
        check = HealCheckResult(
            check_id="fix_imports",
            status=HealStatus.HEALED,
            changes_made=("src/a.py", "src/b.py"),
            rollback_info="git revert abc123",
            notes="Fixed 2 imports",
        )
        result = _minimal_result(results=(check,))
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_to_json_roundtrip(self) -> None:
        result = _minimal_result()
        data = json.loads(result.to_json())
        assert data["tool_id"] == "remediation_dispatcher"
        assert data["contract_version"] == 1

    def test_validate_against_schema_direct(self) -> None:
        result = _minimal_result()
        errors = validate_against_json_schema(result.to_dict())
        assert errors == []


# ---------------------------------------------------------------------------
# Deterministic sorting
# ---------------------------------------------------------------------------


class TestHealContractDeterminism:
    def test_results_sorted_by_check_id(self) -> None:
        result = _minimal_result(
            results=(
                _minimal_check("zebra"),
                _minimal_check("alpha"),
                _minimal_check("middle"),
            ),
        )
        d = result.to_dict()
        ids = [r["check_id"] for r in d["results"]]
        assert ids == ["alpha", "middle", "zebra"]

    def test_approved_by_sorted(self) -> None:
        result = _minimal_result(approved_by=("z_token", "a_token", "m_token"))
        d = result.to_dict()
        assert d["approved_by"] == ["a_token", "m_token", "z_token"]

    def test_changes_made_sorted(self) -> None:
        check = HealCheckResult(
            check_id="fix",
            status=HealStatus.HEALED,
            changes_made=("z/file.py", "a/file.py", "m/file.py"),
        )
        d = check.to_dict()
        assert d["changes_made"] == ["a/file.py", "m/file.py", "z/file.py"]

    def test_idempotent_to_dict(self) -> None:
        result = _minimal_result(
            results=(
                _minimal_check("b"),
                _minimal_check("a"),
            ),
            approved_by=("y", "x"),
        )
        assert result.to_dict() == result.to_dict()


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


class TestHealContractImmutability:
    def test_check_result_frozen(self) -> None:
        check = _minimal_check()
        with pytest.raises(dataclasses.FrozenInstanceError):
            check.check_id = "tampered"

    def test_combined_result_frozen(self) -> None:
        result = _minimal_result()
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.tool_id = "tampered"

    def test_combined_results_tuple_frozen(self) -> None:
        result = _minimal_result()
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.results = ()


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


class TestHealContractNegative:
    def test_invalid_status_rejected(self) -> None:
        with pytest.raises((ValueError, TypeError)):
            HealCheckResult(check_id="test", status="INVALID")

    def test_absolute_path_unix_rejected(self) -> None:
        with pytest.raises(ValueError, match="Absolute path"):
            HealCheckResult(
                check_id="test",
                status=HealStatus.HEALED,
                changes_made=("/usr/local/file.py",),
            )

    def test_absolute_path_windows_rejected(self) -> None:
        with pytest.raises(ValueError, match="Absolute path"):
            HealCheckResult(
                check_id="test",
                status=HealStatus.HEALED,
                changes_made=("C:\\Users\\file.py",),
            )

    def test_empty_check_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="check_id must not be empty"):
            HealCheckResult(check_id="", status=HealStatus.HEALED)

    def test_empty_tool_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="tool_id must not be empty"):
            _minimal_result(tool_id="")

    def test_empty_plan_name_rejected(self) -> None:
        with pytest.raises(ValueError, match="plan_name must not be empty"):
            _minimal_result(plan_name="")

    def test_empty_created_utc_rejected(self) -> None:
        with pytest.raises(ValueError, match="created_utc must not be empty"):
            _minimal_result(created_utc="")

    def test_schema_rejects_extra_key(self) -> None:
        d = _minimal_result().to_dict()
        d["rogue_key"] = "bad"
        errors = validate_against_json_schema(d)
        assert any("unexpected field" in e for e in errors)

    def test_schema_rejects_missing_required(self) -> None:
        d = _minimal_result().to_dict()
        del d["tool_id"]
        errors = validate_against_json_schema(d)
        assert any("missing required" in e for e in errors)

    def test_abs_path_in_schema_validation(self) -> None:
        d = _minimal_result().to_dict()
        d["results"][0]["changes_made"] = ["/absolute/path.py"]
        errors = validate_against_json_schema(d)
        assert any("does not match pattern" in e for e in errors)

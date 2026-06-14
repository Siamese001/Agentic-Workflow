"""Unit tests for agentic_core.L2_execution.types.heal_contract_types.

Wave 6.1 (P2 untested-module coverage) — canonical L2 heal contract.
Covers HealStatus/ClassifierSource enums, HealCheckResult __post_init__ guards
(empty check_id, wrong status type, absolute paths), CombinedHealResult
aggregate guards + deterministic to_dict/to_json, the lightweight schema
validator, and check_schema_compatibility drift detection.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.L2_execution.types.heal_contract_types import (
    CONTRACT_VERSION,
    HEAL_STATUS_VALUES,
    ClassifierSource,
    CombinedHealResult,
    HealCheckResult,
    HealStatus,
    check_schema_compatibility,
    validate_against_json_schema,
)


def _check(**overrides: object) -> HealCheckResult:
    base: dict = {"check_id": "C1", "status": HealStatus.HEALED}
    base.update(overrides)
    return HealCheckResult(**base)  # type: ignore[arg-type]


def _combined(**overrides: object) -> CombinedHealResult:
    base: dict = {
        "tool_id": "tool-x",
        "plan_name": "plan-y",
        "results": (_check(),),
        "approved_by": ("alice",),
        "created_utc": "2026-06-14T00:00:00Z",
    }
    base.update(overrides)
    return CombinedHealResult(**base)  # type: ignore[arg-type]


class TestEnums:
    def test_heal_status_values(self) -> None:
        assert HEAL_STATUS_VALUES == frozenset({"HEALED", "PARTIAL", "FAILED", "SKIPPED"})

    def test_classifier_source_values(self) -> None:
        assert {s.value for s in ClassifierSource} == {"ML_CLASSIFIER", "HEURISTIC_FALLBACK"}

    def test_contract_version(self) -> None:
        assert CONTRACT_VERSION == 2


class TestHealCheckResult:
    def test_defaults(self) -> None:
        c = _check()
        assert c.changes_made == ()
        assert c.rollback_info is None
        assert c.needs_llm_escalation is False

    def test_empty_check_id_raises(self) -> None:
        with pytest.raises(ValueError, match="check_id must not be empty"):
            _check(check_id="")

    def test_non_enum_status_raises(self) -> None:
        with pytest.raises(ValueError, match="status must be a HealStatus"):
            _check(status="HEALED")

    @pytest.mark.parametrize("bad", ["/abs/path", "C:/win/path"])
    def test_absolute_path_in_changes_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="Absolute path not allowed"):
            _check(changes_made=(bad,))

    def test_relative_path_ok(self) -> None:
        c = _check(changes_made=("src/foo.py", "tests/bar.py"))
        assert c.changes_made == ("src/foo.py", "tests/bar.py")

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _check().check_id = "Z"  # type: ignore[misc]

    def test_to_dict_sorts_changes(self) -> None:
        d = _check(changes_made=("z.py", "a.py")).to_dict()
        assert d["changes_made"] == ["a.py", "z.py"]
        assert d["status"] == "HEALED"


class TestCombinedHealResult:
    def test_empty_tool_id_raises(self) -> None:
        with pytest.raises(ValueError, match="tool_id must not be empty"):
            _combined(tool_id="")

    def test_empty_plan_name_raises(self) -> None:
        with pytest.raises(ValueError, match="plan_name must not be empty"):
            _combined(plan_name="")

    def test_empty_created_utc_raises(self) -> None:
        with pytest.raises(ValueError, match="created_utc must not be empty"):
            _combined(created_utc="")

    def test_results_must_be_tuple(self) -> None:
        with pytest.raises(TypeError, match="results must be a tuple"):
            _combined(results=[_check()])

    def test_approved_by_must_be_tuple(self) -> None:
        with pytest.raises(TypeError, match="approved_by must be a tuple"):
            _combined(approved_by=["alice"])

    def test_to_dict_deterministic_ordering(self) -> None:
        d = _combined(
            results=(_check(check_id="C2"), _check(check_id="C1")),
            approved_by=("zed", "amy"),
        ).to_dict()
        assert [r["check_id"] for r in d["results"]] == ["C1", "C2"]
        assert d["approved_by"] == ["amy", "zed"]
        assert d["contract_version"] == CONTRACT_VERSION

    def test_to_json_round_trips(self) -> None:
        c = _combined()
        loaded = json.loads(c.to_json())
        assert loaded == c.to_dict()

    def test_validate_clean_result_has_no_errors(self) -> None:
        assert _combined().validate() == []


class TestSchemaValidators:
    def test_validate_against_json_schema_clean(self) -> None:
        assert validate_against_json_schema(_combined().to_dict()) == []

    def test_validate_missing_required_field(self) -> None:
        d = _combined().to_dict()
        del d["tool_id"]
        errors = validate_against_json_schema(d)
        assert any("tool_id" in e for e in errors)

    def test_validate_rejects_absolute_change_path(self) -> None:
        d = _combined().to_dict()
        d["results"][0]["changes_made"] = ["/abs/x.py"]
        errors = validate_against_json_schema(d)
        assert any("does not match pattern" in e for e in errors)

    def test_check_schema_compatibility_clean(self) -> None:
        assert check_schema_compatibility(_combined().to_dict()) == []

    def test_check_schema_compatibility_detects_extra_key(self) -> None:
        d = _combined().to_dict()
        d["surprise"] = 1
        errors = check_schema_compatibility(d)
        assert any("Unexpected keys" in e for e in errors)

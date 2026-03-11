"""
Contract tests for the L3 Approval contract.

Proves:
1. validate() passes for minimal valid objects.
2. check_schema_compatibility() passes.
3. Deterministic sorting: check_ids sorted, records sorted by token.
4. Negative tests: unknown decision, empty token, empty phase_name rejected.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.L3_orchestration.types.approval_contract_types import (
    ApprovalBundle,
    ApprovalDecision,
    ApprovalRecord,
    check_schema_compatibility,
    validate_against_json_schema,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TIMESTAMP = "2026-02-11T15:00:00Z"


def _minimal_record(**overrides: object) -> ApprovalRecord:
    defaults: dict = {
        "phase_name": "discovery",
        "decision": ApprovalDecision.APPROVED,
        "approver": "admin@example.com",
        "token": "tok_001",
        "created_utc": TIMESTAMP,
    }
    defaults.update(overrides)
    return ApprovalRecord(**defaults)


def _minimal_bundle(**overrides: object) -> ApprovalBundle:
    defaults: dict = {
        "records": (_minimal_record(),),
    }
    defaults.update(overrides)
    return ApprovalBundle(**defaults)


# ---------------------------------------------------------------------------
# Positive: validation passes
# ---------------------------------------------------------------------------


class TestApprovalContractValidation:
    def test_validate_minimal(self) -> None:
        bundle = _minimal_bundle()
        assert bundle.validate() == []

    def test_validate_multiple_records(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_a", phase_name="pre_audit"),
                _minimal_record(
                    token="tok_b",
                    phase_name="healing",
                    decision=ApprovalDecision.REJECTED,
                ),
            ),
        )
        assert bundle.validate() == []

    def test_validate_with_all_fields(self) -> None:
        record = ApprovalRecord(
            phase_name="alignment",
            guardian_id="location_alignment",
            check_ids=("misplaced_files", "missing_directories"),
            decision=ApprovalDecision.APPROVED,
            approver="lead@example.com",
            rationale="All checks reviewed and approved",
            token="tok_full",
            created_utc=TIMESTAMP,
        )
        bundle = ApprovalBundle(records=(record,))
        assert bundle.validate() == []

    def test_schema_compatibility_minimal(self) -> None:
        bundle = _minimal_bundle()
        errors = check_schema_compatibility(bundle.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_to_json_roundtrip(self) -> None:
        bundle = _minimal_bundle()
        data = json.loads(bundle.to_json())
        assert data["contract_version"] == 1
        assert len(data["records"]) == 1

    def test_validate_against_schema_direct(self) -> None:
        bundle = _minimal_bundle()
        errors = validate_against_json_schema(bundle.to_dict())
        assert errors == []


# ---------------------------------------------------------------------------
# Deterministic sorting
# ---------------------------------------------------------------------------


class TestApprovalContractDeterminism:
    def test_records_sorted_by_token(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_z"),
                _minimal_record(token="tok_a"),
                _minimal_record(token="tok_m"),
            ),
        )
        d = bundle.to_dict()
        tokens = [r["token"] for r in d["records"]]
        assert tokens == ["tok_a", "tok_m", "tok_z"]

    def test_check_ids_sorted(self) -> None:
        record = _minimal_record(check_ids=("zebra", "alpha", "middle"))
        d = record.to_dict()
        assert d["check_ids"] == ["alpha", "middle", "zebra"]

    def test_idempotent_to_dict(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_b"),
                _minimal_record(token="tok_a"),
            ),
        )
        assert bundle.to_dict() == bundle.to_dict()

    def test_empty_check_ids_stays_empty(self) -> None:
        record = _minimal_record()
        d = record.to_dict()
        assert d["check_ids"] == []


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


class TestApprovalContractImmutability:
    def test_record_frozen(self) -> None:
        record = _minimal_record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.phase_name = "tampered"

    def test_record_token_frozen(self) -> None:
        record = _minimal_record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.token = "tampered"

    def test_bundle_frozen(self) -> None:
        bundle = _minimal_bundle()
        with pytest.raises(dataclasses.FrozenInstanceError):
            bundle.records = ()


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


class TestApprovalContractNegative:
    def test_unknown_decision_rejected(self) -> None:
        with pytest.raises((ValueError, TypeError)):
            _minimal_record(decision="MAYBE")

    def test_empty_token_rejected(self) -> None:
        with pytest.raises(ValueError, match="token must not be empty"):
            _minimal_record(token="")

    def test_empty_phase_name_rejected(self) -> None:
        with pytest.raises(ValueError, match="phase_name must not be empty"):
            _minimal_record(phase_name="")

    def test_empty_approver_rejected(self) -> None:
        with pytest.raises(ValueError, match="approver must not be empty"):
            _minimal_record(approver="")

    def test_empty_created_utc_rejected(self) -> None:
        with pytest.raises(ValueError, match="created_utc must not be empty"):
            _minimal_record(created_utc="")

    def test_schema_rejects_extra_key(self) -> None:
        d = _minimal_bundle().to_dict()
        d["rogue_key"] = "bad"
        errors = validate_against_json_schema(d)
        assert any("unexpected field" in e for e in errors)

    def test_schema_rejects_missing_required(self) -> None:
        d = _minimal_bundle().to_dict()
        del d["records"]
        errors = validate_against_json_schema(d)
        assert any("missing required" in e for e in errors)

    def test_schema_rejects_invalid_decision_in_dict(self) -> None:
        d = _minimal_bundle().to_dict()
        d["records"][0]["decision"] = "MAYBE"
        errors = validate_against_json_schema(d)
        assert any("not in enum" in e for e in errors)

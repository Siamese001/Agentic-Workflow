"""Tests for OutcomeLogger, OutcomeRecord, OutcomeReconciler (B-modified — GAP-010, G10).

Covers:
- OutcomeRecord.create() — deterministic record_hash
- OutcomeLogger.append() — happy path and record ordering
- OutcomeLogger.records() — immutable snapshot
- OutcomeLogger.append_gate_result() — adapted from ExitGateResult.to_dict()
- OutcomeReconciler.reconcile() — ok/missing/extra logic
"""

import hashlib

import pytest

from agentic_core.L6_observability.enforcement.outcome_logger import (
    OutcomeLogger,
    OutcomeRecord,
    OutcomeReconciler,
)
from agentic_core.L5_safety.types.exit_disposition_types import (
    ExitDisposition,
    ExitEvaluationDimensions,
    ExitGateResult,
)


def _dims(**overrides) -> ExitEvaluationDimensions:
    defaults = dict(
        rules_compliant=True,
        answer_fit=True,
        safety_clear=True,
        grounded_replayable=True,
        confidence_score=0.90,
    )
    defaults.update(overrides)
    return ExitEvaluationDimensions(**defaults)


def _gate_result(**overrides) -> ExitGateResult:
    defaults = dict(
        disposition=ExitDisposition.ALLOW_RESPONSE,
        trace_id="trace-001",
        dimensions=_dims(),
        reason="All dimensions clear.",
        policy_hash="sha256:policy-abc",
    )
    defaults.update(overrides)
    return ExitGateResult(**defaults)


class TestOutcomeRecordCreate:
    def test_create_returns_outcome_record(self):
        r = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        assert isinstance(r, OutcomeRecord)

    def test_record_hash_is_deterministic(self):
        r1 = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        r2 = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        assert r1.record_hash == r2.record_hash

    def test_different_status_different_hash(self):
        r1 = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        r2 = OutcomeRecord.create("t-001", "c-001", "FAILURE", "hash-abc")
        assert r1.record_hash != r2.record_hash

    def test_record_hash_is_sha256_hex(self):
        r = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        assert len(r.record_hash) == 64
        int(r.record_hash, 16)

    def test_outcome_record_is_frozen(self):
        from dataclasses import FrozenInstanceError

        r = OutcomeRecord.create("t-001", "c-001", "SUCCESS", "hash-abc")
        with pytest.raises(FrozenInstanceError):
            r.status = "MODIFIED"  # type: ignore[misc]


class TestOutcomeLoggerAppend:
    def test_append_returns_outcome_record(self):
        logger = OutcomeLogger()
        r = logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="mh-001")
        assert isinstance(r, OutcomeRecord)

    def test_append_records_are_retrievable(self):
        logger = OutcomeLogger()
        logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="mh-001")
        assert len(logger.records()) == 1

    def test_multiple_appends_ordered(self):
        logger = OutcomeLogger()
        logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="h1")
        logger.append(trace_id="t-002", cid="c-002", status="FAILURE", manifest_hash="h2")
        records = logger.records()
        assert len(records) == 2
        assert records[0].trace_id == "t-001"
        assert records[1].trace_id == "t-002"

    def test_records_returns_tuple(self):
        logger = OutcomeLogger()
        logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="h1")
        assert isinstance(logger.records(), tuple)

    def test_empty_logger_returns_empty_tuple(self):
        logger = OutcomeLogger()
        assert logger.records() == ()


class TestOutcomeLoggerAppendGateResult:
    def test_append_gate_result_allow_response(self):
        logger = OutcomeLogger()
        gr = _gate_result(disposition=ExitDisposition.ALLOW_RESPONSE, trace_id="trace-gr-001")
        r = logger.append_gate_result(gr)
        assert r.status == "ALLOW_RESPONSE"
        assert r.trace_id == "trace-gr-001"

    def test_append_gate_result_deny_return(self):
        logger = OutcomeLogger()
        gr = _gate_result(disposition=ExitDisposition.DENY_RETURN, trace_id="trace-deny-001")
        r = logger.append_gate_result(gr)
        assert r.status == "DENY_RETURN"

    def test_append_gate_result_escalate_to_hitl(self):
        logger = OutcomeLogger()
        gr = _gate_result(disposition=ExitDisposition.ESCALATE_TO_HITL, trace_id="trace-hitl-001")
        r = logger.append_gate_result(gr)
        assert r.status == "ESCALATE_TO_HITL"

    def test_append_gate_result_adds_to_records(self):
        logger = OutcomeLogger()
        gr = _gate_result()
        logger.append_gate_result(gr)
        assert len(logger.records()) == 1

    def test_append_gate_result_manifest_hash_non_empty(self):
        logger = OutcomeLogger()
        gr = _gate_result(policy_hash="sha256:policy-xyz")
        r = logger.append_gate_result(gr)
        assert r.manifest_hash and len(r.manifest_hash) > 0

    def test_append_gate_result_no_policy_hash_uses_trace_id(self):
        logger = OutcomeLogger()
        gr = _gate_result(policy_hash=None)
        r = logger.append_gate_result(gr)
        assert r.manifest_hash and len(r.manifest_hash) > 0


class TestOutcomeReconciler:
    def test_reconcile_matching_returns_ok_true(self):
        logger = OutcomeLogger()
        r = logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="h1")
        rec = OutcomeReconciler()
        result = rec.reconcile(observed=logger.records(), expected_hashes=(r.record_hash,))
        assert result.ok is True
        assert result.missing == ()
        assert result.extra == ()

    def test_reconcile_missing_record_flagged(self):
        logger = OutcomeLogger()
        rec = OutcomeReconciler()
        result = rec.reconcile(observed=logger.records(), expected_hashes=("sha256:missing",))
        assert result.ok is False
        assert "sha256:missing" in result.missing

    def test_reconcile_extra_record_flagged(self):
        logger = OutcomeLogger()
        r = logger.append(trace_id="t-001", cid="c-001", status="SUCCESS", manifest_hash="h1")
        rec = OutcomeReconciler()
        result = rec.reconcile(observed=logger.records(), expected_hashes=())
        assert result.ok is False
        assert r.record_hash in result.extra

    def test_reconcile_empty_vs_empty_is_ok(self):
        logger = OutcomeLogger()
        rec = OutcomeReconciler()
        result = rec.reconcile(observed=logger.records(), expected_hashes=())
        assert result.ok is True

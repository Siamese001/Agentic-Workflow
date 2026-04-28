"""
tests/runtime/test_l6_observability_recorder_wireup.py

W9 acceptance: validates the L6 observability_recorder live wire-up.

Targets the three public functions in
``agentic_core.L6_observability.execution.observability_recorder``:
  * ``record_execution_observability``  (success path -> ingest+evaluate)
  * ``record_execution_failure``        (failure -> ingest+evaluate+rca)
  * ``record_policy_block``             (policy block -> ingest+evaluate)

Per the W8 recipe: backward-compat preserved when emitter=None;
when emitter provided, the captured trace passes Phase 5 + Phase 6 +
Phase 7 validators.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.execution import observability_recorder as obs_rec
from agentic_core.L6_observability.execution.observability_recorder import (
    ExecutionContext,
    ExecutionObservabilityContext,
    ExecutionStatus,
    FailureClassification,
)
from agentic_core.runtime.prove_requirements.otel_contract import validate_trace
from agentic_core.runtime.prove_requirements.otel_emitter import RuntimeSpanEmitter
from agentic_core.runtime.prove_requirements.replay_engine import replay_digest


def _exec_ctx(status: ExecutionStatus = ExecutionStatus.SUCCEEDED) -> ExecutionContext:
    return ExecutionContext(
        execution_request_id="req-test-001",
        execution_start_tick=100.0,
        execution_end_tick=100.5,
        execution_status=status,
    )


def _obs_ctx() -> ExecutionObservabilityContext:
    return ExecutionObservabilityContext(
        run_id="run-test-001",
        trace_id="trace-test-001",
        execution_target="test_target",
        guardrail_decision_id="grd-test-001",
        policy_hash="ph-deterministic",
    )


# ---------------------------------------------------------------------------
# Backward-compat: emitter-free paths preserved
# ---------------------------------------------------------------------------

def test_legacy_execution_observability_unchanged() -> None:
    record = obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx())
    assert record.execution_request_id == "req-test-001"
    assert record.execution_status == "SUCCEEDED"
    assert record.replay_key.startswith("rpl-")


def test_legacy_execution_failure_unchanged() -> None:
    record = obs_rec.record_execution_failure(
        _exec_ctx(ExecutionStatus.FAILED),
        _obs_ctx(),
        failure_classification=FailureClassification.TOOL_ERROR,
        failure_reason="provider returned 500",
    )
    assert record.execution_status == "FAILED"
    assert record.failure_classification == "TOOL_ERROR"


def test_legacy_policy_block_unchanged() -> None:
    record = obs_rec.record_policy_block(
        _exec_ctx(ExecutionStatus.BLOCKED_BY_POLICY),
        _obs_ctx(),
        block_reason="content_policy_violation",
    )
    assert record.execution_status == "BLOCKED_BY_POLICY"
    assert record.block_reason == "content_policy_violation"


# ---------------------------------------------------------------------------
# Wired path: success -> ingest + evaluate
# ---------------------------------------------------------------------------

def test_wired_observability_emits_ingest_and_evaluate() -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_l6_obs_success")
    obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e)
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "l6.ingest" in names
    assert "l6.evaluate" in names
    # No RCA on success
    assert "l6.rca_or_proposal" not in names


def test_wired_observability_evaluate_is_child_of_ingest() -> None:
    e = RuntimeSpanEmitter.for_request()
    obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e)
    trace = e.finalize()
    by_name = {s.name: s for s in trace.spans}
    assert by_name["l6.evaluate"].parent_span_id == by_name["l6.ingest"].span_id


def test_wired_observability_replay_key_propagates() -> None:
    """The l6.evaluate span must carry the record's replay_key so future
    replay verification can anchor on this evaluation."""
    e = RuntimeSpanEmitter.for_request()
    record = obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e)
    trace = e.finalize()
    eval_span = next(s for s in trace.spans if s.name == "l6.evaluate")
    assert eval_span.replay_key == record.replay_key


# ---------------------------------------------------------------------------
# Wired path: failure -> ingest + evaluate + rca_or_proposal
# ---------------------------------------------------------------------------

def test_wired_failure_emits_full_chain() -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_l6_failure")
    obs_rec.record_execution_failure(
        _exec_ctx(ExecutionStatus.FAILED),
        _obs_ctx(),
        failure_classification=FailureClassification.TOOL_ERROR,
        failure_reason="upstream timeout",
        emitter=e,
    )
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "l6.ingest" in names
    assert "l6.evaluate" in names
    assert "l6.rca_or_proposal" in names


def test_wired_failure_rca_is_child_of_evaluate() -> None:
    e = RuntimeSpanEmitter.for_request()
    obs_rec.record_execution_failure(
        _exec_ctx(ExecutionStatus.FAILED),
        _obs_ctx(),
        emitter=e,
    )
    trace = e.finalize()
    by_name = {s.name: s for s in trace.spans}
    assert by_name["l6.rca_or_proposal"].parent_span_id == by_name["l6.evaluate"].span_id


def test_wired_failure_carries_classification_in_reason_codes() -> None:
    e = RuntimeSpanEmitter.for_request()
    obs_rec.record_execution_failure(
        _exec_ctx(ExecutionStatus.FAILED),
        _obs_ctx(),
        failure_classification=FailureClassification.POLICY_VIOLATION,
        emitter=e,
    )
    trace = e.finalize()
    rca = next(s for s in trace.spans if s.name == "l6.rca_or_proposal")
    assert "POLICY_VIOLATION" in rca.reason_codes


# ---------------------------------------------------------------------------
# Wired path: policy_block -> ingest + evaluate, NO rca
# ---------------------------------------------------------------------------

def test_wired_policy_block_emits_ingest_and_evaluate_only() -> None:
    e = RuntimeSpanEmitter.for_request()
    obs_rec.record_policy_block(
        _exec_ctx(ExecutionStatus.BLOCKED_BY_POLICY),
        _obs_ctx(),
        block_reason="safety_violation",
        emitter=e,
    )
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "l6.ingest" in names
    assert "l6.evaluate" in names
    # Spec: policy block is governance, not RCA-worthy
    assert "l6.rca_or_proposal" not in names


def test_wired_policy_block_reason_codes() -> None:
    e = RuntimeSpanEmitter.for_request()
    obs_rec.record_policy_block(
        _exec_ctx(ExecutionStatus.BLOCKED_BY_POLICY),
        _obs_ctx(),
        emitter=e,
    )
    trace = e.finalize()
    ingest = next(s for s in trace.spans if s.name == "l6.ingest")
    eval_span = next(s for s in trace.spans if s.name == "l6.evaluate")
    assert "policy_block" in ingest.reason_codes
    assert "policy_block_observed" in eval_span.reason_codes


# ---------------------------------------------------------------------------
# Phase 5 + Phase 6 contract validation on live traces
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["success", "failure", "policy_block"])
def test_wired_traces_pass_phase5_validator(variant: str) -> None:
    e = RuntimeSpanEmitter.for_request(scenario=f"live_l6_{variant}")
    if variant == "success":
        obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e)
    elif variant == "failure":
        obs_rec.record_execution_failure(
            _exec_ctx(ExecutionStatus.FAILED),
            _obs_ctx(),
            emitter=e,
        )
    else:
        obs_rec.record_policy_block(
            _exec_ctx(ExecutionStatus.BLOCKED_BY_POLICY),
            _obs_ctx(),
            emitter=e,
        )
    ok, errs = validate_trace(e.finalize().to_dict())
    assert ok, f"variant={variant} failed Phase 5 validation: {errs}"


def test_wired_replay_determinism_across_runs() -> None:
    """Two calls with the same execution_request_id, run_id, trace_id, and
    policy_hash produce identical deterministic digests (the obs record's
    replay_key is itself deterministic)."""
    e1 = RuntimeSpanEmitter.for_request(scenario="live_l6_replay")
    obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e1)
    e2 = RuntimeSpanEmitter.for_request(scenario="live_l6_replay")
    obs_rec.record_execution_observability(_exec_ctx(), _obs_ctx(), emitter=e2)
    d1 = replay_digest(e1.finalize().to_dict())
    d2 = replay_digest(e2.finalize().to_dict())
    assert d1 == d2, f"replay drift: {d1[:16]}... vs {d2[:16]}..."

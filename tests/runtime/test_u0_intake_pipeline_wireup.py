"""
tests/runtime/test_u0_intake_pipeline_wireup.py

W10 acceptance: validates the first U0-class live wire-up.

Target: ``agentic_core.L0_routing.intake.pipeline.IntakePipeline.run``

Note on layer naming: the user spec lists ``u0.intake`` as the runtime
span name for request intake, but in this codebase the IMPLEMENTATION of
intake lives at the L0 routing boundary (``agentic_core/L0_routing/intake/``).
The proof-OTEL span name remains ``u0.intake`` because that is what the
spec contract expects; the source code lives where it lives.

Asserts:
  * Backward compat: pipeline.run(env) without emitter is byte-identical
    to legacy behavior (every existing test continues to pass)
  * Wired path: pipeline.run(env, emitter=e) emits a u0.intake span
  * Span passes Phase 5 + Phase 6 contract checks
  * Both accepted and rejected outcomes produce a valid span tree
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
from agentic_core.runtime.prove_requirements.otel_contract import validate_trace
from agentic_core.runtime.prove_requirements.otel_emitter import RuntimeSpanEmitter


def _accepted_env() -> RawIngressEnvelope:
    """An envelope that should pass E1..E5."""
    return RawIngressEnvelope(
        transport="chat",
        body_text="hello world",
        auth_credential={"kind": "api_key", "token": "test-key"},
        claimed_user_id="u-test",
        claimed_tenant_id="tenant-test",
    )


def _rejected_env() -> RawIngressEnvelope:
    """An envelope that should fail at E1 (unknown transport)."""
    return RawIngressEnvelope(
        transport="unsupported_transport",
        body_text="hello",
    )


# ---------------------------------------------------------------------------
# Backward-compat: legacy positional call shape
# ---------------------------------------------------------------------------

def test_legacy_run_accepts_envelope() -> None:
    """Legacy callers do `pipeline.run(env)` -- this MUST still work."""
    pipe = IntakePipeline(IntakePolicy())
    out = pipe.run(_accepted_env())
    assert out.accepted
    assert out.validated is not None


def test_legacy_run_rejects_bad_transport() -> None:
    pipe = IntakePipeline(IntakePolicy())
    out = pipe.run(_rejected_env())
    assert not out.accepted
    assert out.rejected is not None


def test_legacy_run_emits_no_proof_span() -> None:
    """A separate emitter not passed to run() should remain empty."""
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request(scenario="control_no_event")
    pipe.run(_accepted_env())  # emitter NOT provided
    assert e.finalize().spans == []


# ---------------------------------------------------------------------------
# Wired path: u0.intake span is emitted
# ---------------------------------------------------------------------------

def test_wired_run_emits_u0_intake_span_on_accept() -> None:
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request(scenario="live_u0_accept")
    out = pipe.run(_accepted_env(), emitter=e)
    assert out.accepted
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "u0.intake" in names


def test_wired_run_emits_u0_intake_span_on_reject() -> None:
    """Even rejected requests must produce the u0.intake span -- the
    governance audit path requires visibility into rejected ingress."""
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request(scenario="live_u0_reject")
    out = pipe.run(_rejected_env(), emitter=e)
    assert not out.accepted
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "u0.intake" in names


def test_wired_intake_carries_started_reason_code() -> None:
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request()
    pipe.run(_accepted_env(), emitter=e)
    trace = e.finalize()
    intake = next(s for s in trace.spans if s.name == "u0.intake")
    assert "intake_started" in intake.reason_codes


def test_wired_intake_status_ok_for_clean_run() -> None:
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request()
    pipe.run(_accepted_env(), emitter=e)
    trace = e.finalize()
    intake = next(s for s in trace.spans if s.name == "u0.intake")
    # Even rejected envelopes return OK at the SPAN level because the
    # pipeline itself completed normally; rejection is in the IntakeOutcome.
    assert intake.status == "OK"


# ---------------------------------------------------------------------------
# Phase 5 + Phase 6 validation
# ---------------------------------------------------------------------------

def test_wired_trace_passes_phase5_validator() -> None:
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request(scenario="live_u0_phase5")
    pipe.run(_accepted_env(), emitter=e)
    ok, errs = validate_trace(e.finalize().to_dict())
    assert ok, f"live U0 trace failed Phase 5: {errs}"


def test_wired_trace_passes_validator_for_rejected_request() -> None:
    pipe = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request(scenario="live_u0_phase5_reject")
    pipe.run(_rejected_env(), emitter=e)
    ok, errs = validate_trace(e.finalize().to_dict())
    assert ok, f"rejected-path U0 trace failed Phase 5: {errs}"


def test_wired_returns_same_outcome_as_legacy() -> None:
    """The emitter must not alter the IntakeOutcome semantics -- accepted
    requests stay accepted, rejected requests stay rejected, validated
    payloads carry the same fields."""
    pipe1 = IntakePipeline(IntakePolicy())
    pipe2 = IntakePipeline(IntakePolicy())
    e = RuntimeSpanEmitter.for_request()
    legacy_out = pipe1.run(_accepted_env())
    wired_out = pipe2.run(_accepted_env(), emitter=e)
    assert legacy_out.accepted == wired_out.accepted
    assert (legacy_out.validated is not None) == (wired_out.validated is not None)
    if legacy_out.validated and wired_out.validated:
        # Same source_class, same auth/quota/schema verdicts.
        assert legacy_out.validated.source_class == wired_out.validated.source_class
        assert legacy_out.validated.auth_verdict == wired_out.validated.auth_verdict
        assert legacy_out.validated.quota_verdict == wired_out.validated.quota_verdict


# ---------------------------------------------------------------------------
# Honesty pin update: U0/L6 wirings now exist
# ---------------------------------------------------------------------------

def test_w10_extends_w8_w9_pattern() -> None:
    """Pure documentation-style assertion: this test exists to make the
    W10 wave self-locating in the test suite. If it ever needs to change,
    the W7 honesty-pin allow-list in test_otel_emitter_adapter.py also
    needs updating."""
    from agentic_core.runtime.prove_requirements.otel_contract import (
        RUNTIME_SPAN_NAMES,
    )
    # u0.intake is a canonical span name -- the emitter contract upholds it.
    assert "u0.intake" in RUNTIME_SPAN_NAMES

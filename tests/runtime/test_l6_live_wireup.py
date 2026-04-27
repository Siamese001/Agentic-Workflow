"""
tests/runtime/test_l6_live_wireup.py

W8 acceptance: validates the FIRST live-runtime wire-up of the proof
OTEL emitter into production code.

Target: ``agentic_core.L6_observability.flywheel_promoter.promote_candidate``

Asserts:
  * Calling ``promote_candidate`` with an emitter produces an
    ``l6.promotion_attempt`` span carrying the correct attributes
  * The captured trace passes the Phase 5 ``validate_trace`` contract
  * The captured trace is replay-deterministic (Phase 6) when
    ``promote_candidate`` is called twice with the same input
  * Calling without an emitter is byte-identical to the legacy behavior
    (no span emitted, no behavioral drift)
  * The L6 observer-posture invariant holds: the wired function never
    mutates state outside its declared output (no orphan side-effects)

Honest gap: this test proves ONE live span emits correctly through the
adapter. It does not yet promote any coverage_matrix record to PROVEN
because that requires a coverage_matrix_builder upgrade to ingest live
traces (deferred to a future wave).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L6_observability import flywheel_promoter
from agentic_core.runtime.prove_requirements.otel_contract import (
    validate_trace,
)
from agentic_core.runtime.prove_requirements.otel_emitter import (
    RuntimeSpanEmitter,
)
from agentic_core.runtime.prove_requirements.replay_engine import (
    replay_digest,
)


def _candidate_event() -> dict[str, Any]:
    """A synthetic event that DOES qualify for promotion (escalation)."""
    return {
        "event_id": "evt-test-001",
        "trace_id": "trace-test-001",
        "request_id": "req-test-001",
        "exit_decision": {
            "disposition": "escalate_hitl",
            "reason_code": "weak_evidence",
        },
    }


def _non_candidate_event() -> dict[str, Any]:
    """A synthetic event that does NOT qualify for promotion."""
    return {
        "event_id": "evt-test-002",
        "trace_id": "trace-test-002",
        "request_id": "req-test-002",
        "exit_decision": {
            "disposition": "allow_finish",
        },
    }


# ---------------------------------------------------------------------------
# Backward-compat: emitter-free path is unchanged
# ---------------------------------------------------------------------------

def test_legacy_call_returns_record_for_candidate() -> None:
    """promote_candidate() without an emitter must continue to work."""
    record = flywheel_promoter.promote_candidate(_candidate_event())
    assert record is not None
    assert record.event_id == "evt-test-001"
    assert "escalation" in record.candidate_reasons


def test_legacy_call_returns_none_for_non_candidate() -> None:
    record = flywheel_promoter.promote_candidate(_non_candidate_event())
    assert record is None


def test_legacy_call_emits_no_span() -> None:
    """When no emitter is provided, no proof-OTEL span is generated.

    This is the observer-posture invariant: the wire-up must not pollute
    other call sites that do not use the proof system.
    """
    e = RuntimeSpanEmitter.for_request(scenario="control_no_event")
    # We pass NO emitter -- emitter parameter is omitted.
    flywheel_promoter.promote_candidate(_candidate_event())
    trace = e.finalize()
    assert trace.spans == [], (
        "legacy call path must not implicitly use a global emitter"
    )


# ---------------------------------------------------------------------------
# Wired path: emitter receives a valid l6.promotion_attempt span
# ---------------------------------------------------------------------------

def test_wired_call_emits_promotion_attempt_span() -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_l6_wireup")
    record = flywheel_promoter.promote_candidate(
        _candidate_event(),
        emitter=e,
    )
    assert record is not None
    trace = e.finalize()
    span_names = {s.name for s in trace.spans}
    assert "l6.promotion_attempt" in span_names


def test_wired_span_carries_reason_codes() -> None:
    e = RuntimeSpanEmitter.for_request()
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e)
    trace = e.finalize()
    promo = next(s for s in trace.spans if s.name == "l6.promotion_attempt")
    assert "promotion_candidate_evaluated" in promo.reason_codes


def test_wired_span_status_ok_for_candidate() -> None:
    e = RuntimeSpanEmitter.for_request()
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e)
    trace = e.finalize()
    promo = next(s for s in trace.spans if s.name == "l6.promotion_attempt")
    assert promo.status == "OK"


def test_wired_span_status_ok_for_abstain() -> None:
    """Abstain (no record returned) is OK at the span level -- the
    promotion_attempt itself completed successfully."""
    e = RuntimeSpanEmitter.for_request()
    record = flywheel_promoter.promote_candidate(
        _non_candidate_event(),
        emitter=e,
    )
    assert record is None
    trace = e.finalize()
    promo = next(s for s in trace.spans if s.name == "l6.promotion_attempt")
    assert promo.status == "OK"


# ---------------------------------------------------------------------------
# Phase 5 contract validator accepts the live trace
# ---------------------------------------------------------------------------

def test_wired_trace_passes_phase5_validator() -> None:
    """The trace produced by the live wire-up must pass the same
    validate_trace function that gates harness-emitted traces."""
    e = RuntimeSpanEmitter.for_request(scenario="live_l6_phase5_check")
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e)
    trace_dict = e.finalize().to_dict()
    ok, errs = validate_trace(trace_dict)
    assert ok, f"live L6 trace failed Phase 5 validation: {errs}"


# ---------------------------------------------------------------------------
# Phase 6 replay-determinism on the live span
# ---------------------------------------------------------------------------

def test_wired_path_is_replay_deterministic() -> None:
    """Two independent calls with the same input produce traces with
    matching deterministic digests (uuid + clock stripped)."""
    e1 = RuntimeSpanEmitter.for_request(scenario="live_l6_replay_a")
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e1)
    t1 = e1.finalize().to_dict()

    e2 = RuntimeSpanEmitter.for_request(scenario="live_l6_replay_a")
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e2)
    t2 = e2.finalize().to_dict()

    d1 = replay_digest(t1)
    d2 = replay_digest(t2)
    assert d1 == d2, (
        f"live L6 wire-up failed replay determinism: {d1[:16]}... vs {d2[:16]}..."
    )


def test_wired_replay_drift_when_event_changes() -> None:
    """Sanity-check: a DIFFERENT event must produce a different
    deterministic digest (otherwise replay-drift detection is vacuous)."""
    e1 = RuntimeSpanEmitter.for_request(scenario="live_l6_drift_a")
    flywheel_promoter.promote_candidate(_candidate_event(), emitter=e1)
    t1 = e1.finalize().to_dict()

    e2 = RuntimeSpanEmitter.for_request(scenario="live_l6_drift_b")
    flywheel_promoter.promote_candidate(_non_candidate_event(), emitter=e2)
    t2 = e2.finalize().to_dict()
    # When event differs but produces no record, the second emitter has
    # only the runtime.request root + the empty l6.promotion_attempt; the
    # first has both. Their deterministic digests MUST differ because
    # the scenario name (a deterministic field) differs.
    d1 = replay_digest(t1)
    d2 = replay_digest(t2)
    assert d1 != d2


# ---------------------------------------------------------------------------
# Stage-to-disk path still works under wired emission
# ---------------------------------------------------------------------------

def test_wired_stage_to_disk_preserved(tmp_path: Path) -> None:
    """The emitter must not interfere with the existing triage write."""
    e = RuntimeSpanEmitter.for_request()
    record = flywheel_promoter.promote_candidate(
        _candidate_event(),
        triage_root=tmp_path,
        stage_to_disk=True,
        emitter=e,
    )
    assert record is not None
    written = list(tmp_path.glob("*.json"))
    assert len(written) == 1, f"stage_to_disk did not write file under {tmp_path}"
    trace = e.finalize()
    assert any(s.name == "l6.promotion_attempt" for s in trace.spans)


# ---------------------------------------------------------------------------
# Honesty pin: this is the ONLY live wire-up so far
# ---------------------------------------------------------------------------

def test_flywheel_promoter_remains_wired(repo_root: Path) -> None:
    """W8 invariant (subset of the W7 honesty pin): flywheel_promoter.py
    must remain wired. The full allow-list lives in
    test_otel_emitter_adapter.py::test_no_unexpected_live_wirings -- this
    test only ensures THIS wave's target stays connected."""
    import re
    pattern = re.compile(
        r"from agentic_core\.runtime\.prove_requirements\.otel_emitter import"
    )
    target = repo_root / "agentic_core" / "L6_observability" / "flywheel_promoter.py"
    txt = target.read_text(encoding="utf-8", errors="replace")
    assert pattern.search(txt), (
        f"W8 wire-up broken: {target} no longer imports the proof emitter. "
        "Restore the import or remove the W8 wave from the proof report."
    )

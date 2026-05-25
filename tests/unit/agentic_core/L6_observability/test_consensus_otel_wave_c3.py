"""Wave C3 tests — consensus.v1 OTEL emitter.

Plan: `.windsurf/plans/consensus-validator-unification-5e9f3a.md` Wave C3.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.consensus_otel import (
    REQUIRED_JUDGE_ATTRIBUTES,
    REQUIRED_JUROR_ATTRIBUTES,
    SPAN_NAME_JUDGE,
    SPAN_NAME_JUROR,
    SPAN_NAME_VERDICT,
    ConsensusJudgeRecord,
    ConsensusTelemetryEmitter,
    JurorVoteRecord,
    get_default_emitter,
)

pytestmark = pytest.mark.unit


def _fresh_emitter():
    """Reset module singleton for test isolation."""
    from agentic_core.L6_observability import consensus_otel as mod  # noqa: PLC0415

    mod._default_emitter = None  # noqa: SLF001
    emitter = get_default_emitter()
    emitter.clear()
    return emitter


def test_span_name_constants_follow_consensus_v1_scheme():
    assert SPAN_NAME_JUDGE == "consensus.v1.judge"
    assert SPAN_NAME_JUROR == "consensus.v1.juror"
    assert SPAN_NAME_VERDICT == "consensus.v1.verdict"


def test_required_attribute_sets_defined():
    assert "consensus.trace_id" in REQUIRED_JUDGE_ATTRIBUTES
    assert "consensus.juror_count" in REQUIRED_JUDGE_ATTRIBUTES
    assert "consensus.threshold" in REQUIRED_JUDGE_ATTRIBUTES
    assert "consensus.verdict" in REQUIRED_JUDGE_ATTRIBUTES
    assert "consensus.artifact_hash" in REQUIRED_JUDGE_ATTRIBUTES
    assert "consensus.juror_model" in REQUIRED_JUROR_ATTRIBUTES
    assert "consensus.juror_verdict" in REQUIRED_JUROR_ATTRIBUTES


def test_emit_judge_span_captures_record():
    emitter = _fresh_emitter()
    votes = [
        JurorVoteRecord(
            consensus_trace_id="x",
            juror_model="j1",
            juror_verdict="YES",
            reason="ok",
            timestamp=1.0,
        ),
        JurorVoteRecord(
            consensus_trace_id="x",
            juror_model="j2",
            juror_verdict="YES",
            reason="ok",
            timestamp=1.1,
        ),
        JurorVoteRecord(
            consensus_trace_id="x",
            juror_model="j3",
            juror_verdict="NO",
            reason="regression",
            timestamp=1.2,
        ),
    ]
    record = emitter.emit_judge_span(
        juror_count=3,
        threshold=2 / 3,
        verdict="APPROVED",
        artifact_hash="abc123",
        juror_votes=votes,
    )

    assert isinstance(record, ConsensusJudgeRecord)
    assert record.juror_count == 3
    assert record.verdict == "APPROVED"
    assert record.artifact_hash == "abc123"
    assert len(record.juror_votes) == 3
    assert record.consensus_trace_id  # uuid auto-generated


def test_to_span_attributes_contains_all_required():
    record = ConsensusJudgeRecord(
        consensus_trace_id="t1",
        timestamp=100.0,
        juror_count=3,
        threshold=2 / 3,
        verdict="REJECTED",
        artifact_hash="h1",
    )
    attrs = record.to_span_attributes()
    for required in REQUIRED_JUDGE_ATTRIBUTES:
        assert required in attrs, f"Missing required attribute: {required}"


def test_custom_trace_id_is_preserved():
    emitter = _fresh_emitter()
    rec = emitter.emit_judge_span(
        consensus_trace_id="deadbeef",
        juror_count=3,
        threshold=2 / 3,
        verdict="APPROVED",
        artifact_hash="h",
    )
    assert rec.consensus_trace_id == "deadbeef"


def test_ring_buffer_caps_at_max_size():
    emitter = ConsensusTelemetryEmitter()
    emitter._MAX_RING_SIZE = 5  # noqa: SLF001  — test-only cap
    for i in range(10):
        emitter.emit_judge_span(
            juror_count=3,
            threshold=2 / 3,
            verdict="APPROVED",
            artifact_hash=f"h{i}",
        )
    assert len(emitter) == 5


def test_recent_returns_most_recent_records():
    emitter = _fresh_emitter()
    for i in range(3):
        emitter.emit_judge_span(
            juror_count=3,
            threshold=2 / 3,
            verdict="APPROVED",
            artifact_hash=f"h{i}",
        )
    recent = emitter.recent(limit=2)
    assert len(recent) == 2
    assert recent[-1].artifact_hash == "h2"


def test_clear_empties_ring():
    emitter = _fresh_emitter()
    emitter.emit_judge_span(
        juror_count=3,
        threshold=2 / 3,
        verdict="APPROVED",
        artifact_hash="h",
    )
    assert len(emitter) == 1
    emitter.clear()
    assert len(emitter) == 0


def test_default_emitter_is_singleton():
    a = get_default_emitter()
    b = get_default_emitter()
    assert a is b


def test_emission_best_effort_when_tracer_raises():
    """OTEL tracer failures must not raise out of emit_judge_span."""
    emitter = _fresh_emitter()

    class _BrokenTracer:
        def start_as_current_span(self, *_a, **_kw):  # noqa: ARG002
            raise RuntimeError("simulated tracer failure")

    emitter._otel_tracer = _BrokenTracer()  # noqa: SLF001
    # Should NOT raise
    rec = emitter.emit_judge_span(
        juror_count=3,
        threshold=2 / 3,
        verdict="APPROVED",
        artifact_hash="h",
    )
    assert rec.verdict == "APPROVED"


def test_h5_placeholder_symbols_deleted():
    """H5 M2-M4 guard: the 3 placeholder symbols in system_learning/confidence/engine.py are gone."""
    import agentic_core.L6_system_learning.confidence.engine as mod  # noqa: PLC0415

    assert not hasattr(mod, "CONFIDENCE_THRESHOLD"), "H5 M2-M4 incomplete: CONFIDENCE_THRESHOLD still present"
    assert not hasattr(mod, "calculate_confidence"), "H5 M2-M4 incomplete: calculate_confidence still present"
    # The real HealingConfidenceScorer class must remain
    assert hasattr(mod, "HealingConfidenceScorer")

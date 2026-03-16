"""
Phase 2 Wave 2 — RetrievalAnchor Tests

Tests that:
- RetrievalAnchor requires all fields
- AnchoredResult pairs content with anchor
- enforce_anchor_coverage blocks unanchored retrieval use
- Negative: reasoning without anchors raises AnchorViolationError
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.retrieval_anchor_types import (
    AnchoredResult,
    AnchorViolationError,
    RetrievalAnchor,
    enforce_anchor_coverage,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_retrieval_anchors")
_emit_applies_guardrail("p0", "test_retrieval_anchors", "p0_governance")
_emit_reads_policy_state("p0", "test_retrieval_anchors", "policy_binding")
_emit_snapshots_state("p0", "test_retrieval_anchors", "state_snapshot")
emit_replay_key("p0", "test_retrieval_anchors")
emit_determinism_digest("p0", "test_retrieval_anchors")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_retrieval_anchors", "execution_auth")
_emit_validates_capability("p2", "test_retrieval_anchors", "capability_check")
_emit_routes_to_capability("p2", "test_retrieval_anchors", "capability_route")
_emit_writes_via_uwg("p2", "test_retrieval_anchors", "uwg_write")
_emit_blocks_direct_write("p2", "test_retrieval_anchors", "direct_write_block")
_emit_records_tool_invocation("p2", "test_retrieval_anchors", "tool_invocation")
_emit_captures_execution_output("p2", "test_retrieval_anchors", "exec_output")
_emit_dispatches_agent("p3", "test_retrieval_anchors", "agent_dispatch")
_emit_coordinates_agents("p3", "test_retrieval_anchors", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_retrieval_anchors", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_retrieval_anchors", "healing_outcome")
_emit_escalates_failure("p3", "test_retrieval_anchors", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_retrieval_anchors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_retrieval_anchors", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_retrieval_anchors", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_retrieval_anchors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_retrieval_anchors", "eval_metric")
_emit_stores_embedding("p4", "test_retrieval_anchors", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_retrieval_anchors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_retrieval_anchors", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


def _make_anchor(
    source_doc_id: str = "doc-001",
    chunk_id: str = "chunk-001",
    char_start: int = 0,
    char_end: int = 100,
    version_hash: str = "abc123",
) -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=char_start,
        char_end=char_end,
        retrieved_at_utc=RetrievalAnchor.now_utc(),
        version_hash=version_hash,
    )


class TestRetrievalAnchor:
    def test_retrieval_returns_anchors(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="some retrieved text", anchor=anchor)
        assert result.anchor.source_doc_id == "doc-001"
        assert result.anchor.chunk_id == "chunk-001"
        assert result.anchor.char_start == 0
        assert result.anchor.char_end == 100
        assert result.anchor.version_hash == "abc123"
        assert result.anchor.retrieved_at_utc

    def test_anchor_to_dict_has_all_fields(self):
        anchor = _make_anchor()
        d = anchor.to_dict()
        assert set(d.keys()) == {
            "source_doc_id",
            "chunk_id",
            "char_start",
            "char_end",
            "retrieved_at_utc",
            "version_hash",
        }

    def test_anchor_rejects_empty_source_doc_id(self):
        with pytest.raises(ValueError, match="source_doc_id"):
            RetrievalAnchor(
                source_doc_id="",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_chunk_id(self):
        with pytest.raises(ValueError, match="chunk_id"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_inverted_offsets(self):
        with pytest.raises(ValueError, match="char_end"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=100,
                char_end=50,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_version_hash(self):
        with pytest.raises(ValueError, match="version_hash"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="",
            )


class TestAnchorCoverageEnforcement:
    def test_empty_retrieval_context_passes_with_no_anchors(self):
        enforce_anchor_coverage([], [])

    def test_reasoning_requires_anchors_when_retrieval_present(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert AnchorViolationError.VIOLATION_CODE in str(exc_info.value)
        assert "empty" in str(exc_info.value)

    def test_reasoning_without_anchors_is_rejected(self):
        anchor = _make_anchor(chunk_id="chunk-A")
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert "MISSING_RETRIEVAL_ANCHOR" in str(exc_info.value)

    def test_uncovered_chunk_raises_violation(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        with pytest.raises(AnchorViolationError, match="chunk-B"):
            enforce_anchor_coverage([result_a, result_b], [anchor_a])

    def test_full_coverage_passes(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        enforce_anchor_coverage([result_a, result_b], [anchor_a, anchor_b])

    def test_violation_error_code_is_constant(self):
        assert AnchorViolationError.VIOLATION_CODE == "MISSING_RETRIEVAL_ANCHOR"

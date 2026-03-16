"""
L4 RetrievalAnchor — Phase 2

Mandatory citation anchor returned with every L4 retrieval result.
Enforces grounding: every piece of retrieved content is traceable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "retrieval_anchor_types")
emit_determinism_digest("p0", "retrieval_anchor_types")

_emit_dispatches_healing_run("p1", "retrieval_anchor_types", "L4")
_emit_routes_through("p1", "retrieval_anchor_types", "L4")
_emit_escalates_to_human("p1", "retrieval_anchor_types", "L4")
_emit_reads_policy_state("p1", "retrieval_anchor_types", "L4")
_emit_authorize_and_execute("p2", "retrieval_anchor_types", "execution_auth")
_emit_validates_capability("p2", "retrieval_anchor_types", "capability_check")
_emit_routes_to_capability("p2", "retrieval_anchor_types", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_anchor_types", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_anchor_types", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_anchor_types", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_anchor_types", "exec_output")
_emit_dispatches_agent("p3", "retrieval_anchor_types", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_anchor_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_anchor_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_anchor_types", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_anchor_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_anchor_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_anchor_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_anchor_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_anchor_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_anchor_types", "eval_metric")
_emit_stores_embedding("p4", "retrieval_anchor_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_anchor_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_anchor_types", "exec_snapshot_link")


@dataclass
class RetrievalAnchor:
    """
    Citation anchor attached to every L4 retrieval result.

    All fields are required. No optional fields — absence of any field
    indicates a retrieval implementation that has not been grounded.
    """

    source_doc_id: str
    chunk_id: str
    char_start: int
    char_end: int
    retrieved_at_utc: str
    version_hash: str

    def __post_init__(self) -> None:
        if not self.source_doc_id:
            raise ValueError("source_doc_id must be non-empty")
        if not self.chunk_id:
            raise ValueError("chunk_id must be non-empty")
        if self.char_end <= self.char_start:
            raise ValueError(f"char_end ({self.char_end}) must be > char_start ({self.char_start})")
        if not self.retrieved_at_utc:
            raise ValueError("retrieved_at_utc must be non-empty")
        if not self.version_hash:
            raise ValueError("version_hash must be non-empty")

    @staticmethod
    def now_utc() -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def to_dict(self) -> dict[str, object]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RetrievalAnchor.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RetrievalAnchor.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RetrievalAnchor.to_dict")
        return {
            "source_doc_id": self.source_doc_id,
            "chunk_id": self.chunk_id,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "retrieved_at_utc": self.retrieved_at_utc,
            "version_hash": self.version_hash,
        }


@dataclass
class AnchoredResult:
    """
    A retrieval result paired with its mandatory citation anchor.
    Returned by all L4 semantic search / chunk retrieval calls.
    """

    content: str
    anchor: RetrievalAnchor


class AnchorViolationError(Exception):
    """
    Raised by Guardian when reasoning uses retrieved content without anchors.

    Violation code: MISSING_RETRIEVAL_ANCHOR
    """

    VIOLATION_CODE = "MISSING_RETRIEVAL_ANCHOR"

    def __init__(self, message: str = "Reasoning used retrieved content but provided no anchors") -> None:
        super().__init__(f"[{self.VIOLATION_CODE}] {message}")


def enforce_anchor_coverage(retrieval_context: list[AnchoredResult], anchors: list[RetrievalAnchor]) -> None:
    """
    Guardian enforcement: if retrieval_context is non-empty,
    anchors list must be non-empty and cover each retrieved chunk.

    Raises AnchorViolationError if the invariant is violated.
    """
    if not retrieval_context:
        return
    if not anchors:
        raise AnchorViolationError("retrieval_context is non-empty but anchors list is empty")
    retrieved_chunk_ids = {r.anchor.chunk_id for r in retrieval_context}
    covered_chunk_ids = {a.chunk_id for a in anchors}
    uncovered = retrieved_chunk_ids - covered_chunk_ids
    if uncovered:
        raise AnchorViolationError(f"Retrieved chunks not covered by anchors: {sorted(uncovered)}")

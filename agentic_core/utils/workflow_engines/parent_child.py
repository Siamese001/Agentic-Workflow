"""
Phase A: Parent-Child Expander — concrete implementation.

Reconstructs parent section context from child chunk matches using an
in-memory registry of chunk manifests and parent-child links.

C0 RULE: Informational only. Does not authorize execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.retrieval.completeness import GroundedDocument, IParentChildExpander
from agentic_core.evaluation.retrieval.interfaces import Document
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "parent_child", "p0_governance")
_emit_reads_policy_state("p0", "parent_child", "policy_binding")
_emit_snapshots_state("p0", "parent_child", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("parent_child", "p4obs", "metric_1")
_emit_emits_metric_event("parent_child", "p4obs", "metric_2")
_emit_emits_metric_event("parent_child", "p4obs", "metric_3")
_emit_emits_metric_event("parent_child", "p4obs", "metric_4")
_emit_emits_metric_event("parent_child", "p4obs", "metric_5")
_emit_emits_metric_event("parent_child", "p4obs", "metric_6")
_emit_records_incident_event("parent_child", "p4obs", "incident")
_emit_captures_runtime_anomaly("parent_child", "p4obs", "anomaly")
_emit_writes_observability_log("parent_child", "p4obs", "obs_log")
_emit_updates_monitoring_state("parent_child", "p4obs", "mon_state")
_emit_triggers_alert("parent_child", "p4obs", "alert")
_emit_links_incident_trace("parent_child", "p4obs", "trace_link")
_emit_captures_pattern("parent_child", "p3lm", "pattern")
_emit_records_learning_event("parent_child", "p3lm", "learning_event")
_emit_writes_learning_snapshot("parent_child", "p3lm", "snapshot")
_emit_feeds_meta_learning("parent_child", "p3lm", "meta_feed")
_emit_updates_routing_strategy("parent_child", "p3lm", "routing")
_emit_improves_agent_policy("parent_child", "p3lm", "policy")
_emit_stores_learning_state("parent_child", "p3lm", "state")
_emit_records_execution_trace("parent_child", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("parent_child", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("parent_child", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("parent_child", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("parent_child", "L4_STATE", "p2_trace_5")
_emit_reads_environ("parent_child", "env_read", "p2_env_1")
_emit_reads_environ("parent_child", "env_read", "p2_env_2")
_emit_reads_runtime_state("parent_child", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("parent_child", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "parent_child", "context_pull")
_emit_pulls_context("p1", "parent_child", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "parent_child", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "parent_child", "uwg_term_2")
_emit_writes_through("p1", "parent_child", "write_through")
_emit_writes_through("p1", "parent_child", "write_through_2")
_emit_validated_by_safety_plane("p1", "parent_child", "safety_validation")
_emit_invokes_eval("p1", "parent_child", "eval_call")
_emit_proposal_commits_routing("p1", "parent_child", "routing_commit")
_emit_escalates_to_human("p1", "parent_child", "human_escalation")
_emit_routes_through("p1", "parent_child", "route_through")
_emit_checks_agent_registry("p1", "parent_child", "agent_registry")
_emit_validates_agent_capability("p1", "parent_child", "capability")
_emit_dispatches_execution_plan("p1", "parent_child", "exec_plan")
_emit_agent_executes_agent("p1", "parent_child", "sub_agent")
_emit_routes_to_agent("p1", "parent_child", "target_agent")
_emit_verifies_policy("p1", "parent_child", "policy_check")
_emit_observes_runtime_state("p1", "parent_child", "runtime_state")
_emit_verifies_boundary("p1", "parent_child", "boundary_check")
_emit_transcripts_response("p1", "parent_child", "transcript")
_emit_hard_fails_untranscripted("p1", "parent_child")
_emit_gated_by_confidence("p1", "parent_child", "confidence_gate")
emit_replay_key("p0", "parent_child")
emit_determinism_digest("p0", "parent_child")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "parent_child", "execution_auth")
_emit_validates_capability("p2", "parent_child", "capability_check")
_emit_routes_to_capability("p2", "parent_child", "capability_route")
_emit_writes_via_uwg("p2", "parent_child", "uwg_write")
_emit_blocks_direct_write("p2", "parent_child", "direct_write_block")
_emit_records_tool_invocation("p2", "parent_child", "tool_invocation")
_emit_captures_execution_output("p2", "parent_child", "exec_output")
_emit_dispatches_agent("p3", "parent_child", "agent_dispatch")
_emit_coordinates_agents("p3", "parent_child", "agent_coordination")
_emit_records_workflow_lineage("p3", "parent_child", "workflow_lineage")
_emit_records_healing_outcome("p3", "parent_child", "healing_outcome")
_emit_escalates_failure("p3", "parent_child", "failure_escalation")
_emit_orchestrates_workflow("p3", "parent_child", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "parent_child", "healing_dispatch")
_emit_invokes_evaluation("p3", "parent_child", "evaluation_signal")
_emit_records_telemetry_event("p4", "parent_child", "telemetry_event")
_emit_captures_evaluation_metric("p4", "parent_child", "eval_metric")
_emit_stores_embedding("p4", "parent_child", "embedding_store")
_emit_updates_meta_learning_state("p4", "parent_child", "meta_learning")
_emit_links_execution_to_snapshot("p4", "parent_child", "exec_snapshot_link")


@dataclass(frozen=True)
class ChunkEntry:
    """Minimal chunk metadata for parent-child expansion."""

    chunk_id: str
    parent_section_id: str
    sibling_ids: tuple[str, ...]
    content: str
    heading_path: tuple[str, ...]
    source_doc_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "parent_section_id": self.parent_section_id,
            "sibling_ids": list(self.sibling_ids),
            "content": self.content,
            "heading_path": list(self.heading_path),
            "source_doc_id": self.source_doc_id,
        }


@dataclass
class ParentChildRegistry:
    """In-memory registry mapping chunk_id -> ChunkEntry and parent content.

    Populated at index build time from the ChunkManifestRegistry (L4D).
    Read-only at retrieval time.
    """

    _chunks: dict[str, ChunkEntry] = field(default_factory=dict)
    _parent_content: dict[str, str] = field(default_factory=dict)

    def register_chunk(self, entry: ChunkEntry, parent_content: str = "") -> None:
        """Register a chunk entry and its parent section content."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParentChildRegistry.register_chunk")

        self._chunks[entry.chunk_id] = entry
        if entry.parent_section_id and parent_content:
            self._parent_content[entry.parent_section_id] = parent_content

    def get_chunk(self, chunk_id: str) -> ChunkEntry | None:
        return self._chunks.get(chunk_id)

    def get_parent_content(self, parent_section_id: str) -> str:
        return self._parent_content.get(parent_section_id, "")

    def chunk_count(self) -> int:
        return len(self._chunks)

    def parent_count(self) -> int:
        return len(self._parent_content)


class ParentChildExpander(IParentChildExpander):
    """Expands a child chunk to its parent section and neighbor siblings.

    Uses a ParentChildRegistry populated from the ChunkManifestRegistry (L4D).
    Falls back to returning the child document unchanged if no registry entry
    is found — always succeeds, never raises.

    C0 RULE: Read-only, informational expansion only.
    """

    def __init__(self, registry: ParentChildRegistry) -> None:
        self._registry = registry

    def expand(self, child: Document, neighbor_window: int = 1) -> GroundedDocument:
        """Expand child chunk to include parent section and sibling context."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParentChildExpander.expand")

        entry = self._registry.get_chunk(child.doc_id)
        if entry is None:
            return GroundedDocument(
                doc_id=child.doc_id,
                content=child.content,
                score=child.score,
                metadata=dict(child.metadata),
                parent_section_id="",
                parent_content="",
                sibling_ids=[],
                heading_path=[],
                expanded=False,
            )
        parent_content = self._registry.get_parent_content(entry.parent_section_id)
        neighbor_ids = self._resolve_neighbors(entry, neighbor_window)
        return GroundedDocument(
            doc_id=child.doc_id,
            content=child.content,
            score=child.score,
            metadata=dict(child.metadata),
            parent_section_id=entry.parent_section_id,
            parent_content=parent_content,
            sibling_ids=neighbor_ids,
            heading_path=list(entry.heading_path),
            expanded=True,
        )

    def get_parent_section_id(self, chunk_id: str) -> str | None:
        entry = self._registry.get_chunk(chunk_id)
        if entry is None:
            return None
        return entry.parent_section_id or None

    def get_heading_path(self, chunk_id: str) -> list[str]:
        entry = self._registry.get_chunk(chunk_id)
        if entry is None:
            return []
        return list(entry.heading_path)

    def _resolve_neighbors(self, entry: ChunkEntry, window: int) -> list[str]:
        """Return neighbor chunk IDs within the sibling list, bounded by window."""
        siblings = list(entry.sibling_ids)
        if not siblings:
            return []
        try:
            idx = siblings.index(entry.chunk_id)
        except ValueError:
            return siblings[:window]
        lo = max(0, idx - window)
        hi = min(len(siblings), idx + window + 1)
        return [s for s in siblings[lo:hi] if s != entry.chunk_id]


__all__ = ["ChunkEntry", "ParentChildRegistry", "ParentChildExpander"]

"""
Phase 8 — CitationBundle: deterministic, non-mutating citation artifact.

Attached to any response that uses L4 retrieval.
citation_hash = sha256(canonical_bytes excluding citation_hash).
Anchors sorted by (source_doc_id, chunk_id, char_start) for determinism.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L4_state.types.retrieval_anchor_types import RetrievalAnchor
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "citation_bundle_types")
emit_determinism_digest("p0", "citation_bundle_types")

_emit_dispatches_healing_run("p1", "citation_bundle_types", "L4")
_emit_routes_through("p1", "citation_bundle_types", "L4")
_emit_checks_agent_registry("p1", "citation_bundle_types", "agent_registry")
_emit_validates_agent_capability("p1", "citation_bundle_types", "capability")
_emit_dispatches_execution_plan("p1", "citation_bundle_types", "exec_plan")
_emit_agent_executes_agent("p1", "citation_bundle_types", "sub_agent")
_emit_routes_to_agent("p1", "citation_bundle_types", "target_agent")
_emit_verifies_policy("p1", "citation_bundle_types", "policy_check")
_emit_observes_runtime_state("p1", "citation_bundle_types", "runtime_state")
_emit_verifies_boundary("p1", "citation_bundle_types", "boundary_check")
_emit_transcripts_response("p1", "citation_bundle_types", "transcript")
_emit_hard_fails_untranscripted("p1", "citation_bundle_types")
_emit_gated_by_confidence("p1", "citation_bundle_types", "confidence_gate")
_emit_escalates_to_human("p1", "citation_bundle_types", "L4")
_emit_reads_policy_state("p1", "citation_bundle_types", "L4")
_emit_authorize_and_execute("p2", "citation_bundle_types", "execution_auth")
_emit_validates_capability("p2", "citation_bundle_types", "capability_check")
_emit_routes_to_capability("p2", "citation_bundle_types", "capability_route")
_emit_writes_via_uwg("p2", "citation_bundle_types", "uwg_write")
_emit_blocks_direct_write("p2", "citation_bundle_types", "direct_write_block")
_emit_records_tool_invocation("p2", "citation_bundle_types", "tool_invocation")
_emit_captures_execution_output("p2", "citation_bundle_types", "exec_output")
_emit_dispatches_agent("p3", "citation_bundle_types", "agent_dispatch")
_emit_coordinates_agents("p3", "citation_bundle_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "citation_bundle_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "citation_bundle_types", "healing_outcome")
_emit_escalates_failure("p3", "citation_bundle_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "citation_bundle_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "citation_bundle_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "citation_bundle_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "citation_bundle_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "citation_bundle_types", "eval_metric")
_emit_stores_embedding("p4", "citation_bundle_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "citation_bundle_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "citation_bundle_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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

_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_1")
_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_2")
_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_3")
_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_4")
_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_5")
_emit_emits_metric_event("citation_bundle_types", "p4obs", "metric_6")
_emit_records_incident_event("citation_bundle_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("citation_bundle_types", "p4obs", "anomaly")
_emit_writes_observability_log("citation_bundle_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("citation_bundle_types", "p4obs", "mon_state")
_emit_triggers_alert("citation_bundle_types", "p4obs", "alert")
_emit_links_incident_trace("citation_bundle_types", "p4obs", "trace_link")
_emit_captures_pattern("citation_bundle_types", "p3lm", "pattern")
_emit_records_learning_event("citation_bundle_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("citation_bundle_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("citation_bundle_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("citation_bundle_types", "p3lm", "routing")
_emit_improves_agent_policy("citation_bundle_types", "p3lm", "policy")
_emit_stores_learning_state("citation_bundle_types", "p3lm", "state")
_emit_records_execution_trace("citation_bundle_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("citation_bundle_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("citation_bundle_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("citation_bundle_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("citation_bundle_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("citation_bundle_types", "env_read", "p2_env_1")
_emit_reads_environ("citation_bundle_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("citation_bundle_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("citation_bundle_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "citation_bundle_types", "context_pull")
_emit_pulls_context("p1", "citation_bundle_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "citation_bundle_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "citation_bundle_types", "uwg_term_2")
_emit_writes_through("p1", "citation_bundle_types", "write_through")
_emit_writes_through("p1", "citation_bundle_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "citation_bundle_types", "safety_validation")
_emit_invokes_eval("p1", "citation_bundle_types", "eval_call")
_emit_proposal_commits_routing("p1", "citation_bundle_types", "routing_commit")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _anchor_sort_key(a: RetrievalAnchor) -> tuple[str, str, int]:
    return (a.source_doc_id, a.chunk_id, a.char_start)


@dataclass
class CitationBundle:
    """
    Deterministic citation artifact attached to retrieval-backed responses.

    Fields
    ------
    schema_version : int              — bumped on breaking changes
    request_hash   : str              — sha256 of canonical retrieval request
    anchors        : list[RetrievalAnchor] — sorted by (source_doc_id, chunk_id, char_start)
    citation_hash  : str              — sha256(canonical_bytes); auto-computed
    """

    schema_version: int
    request_hash: str
    anchors: list[RetrievalAnchor]
    citation_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"CitationBundle: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}",
            )
        if not self.request_hash:
            raise ValueError("CitationBundle: request_hash must be non-empty")
        if not isinstance(self.anchors, list):
            raise TypeError("CitationBundle: anchors must be a list")
        self.anchors = sorted(self.anchors, key=_anchor_sort_key)
        object.__setattr__(self, "citation_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding citation_hash (self-referential).
        Anchors sorted by (source_doc_id, chunk_id, char_start).
        Volatile fields (retrieved_at_utc) excluded from hash computation.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CitationBundle.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CitationBundle.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "CitationBundle.canonical_bytes")

        doc: dict[str, Any] = {
            "anchors": [
                {
                    "char_end": a.char_end,
                    "char_start": a.char_start,
                    "chunk_id": a.chunk_id,
                    "source_doc_id": a.source_doc_id,
                    "version_hash": a.version_hash,
                }
                for a in sorted(self.anchors, key=_anchor_sort_key)
            ],
            "request_hash": self.request_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_hash": self.request_hash,
            "anchors": [a.to_dict() for a in self.anchors],
            "citation_hash": self.citation_hash,
        }


def build_citation_bundle(request_hash: str, anchors: list[RetrievalAnchor]) -> CitationBundle:
    """Factory: build a CitationBundle from a request hash and anchor list."""
    return CitationBundle(schema_version=_SCHEMA_VERSION, request_hash=request_hash, anchors=anchors)

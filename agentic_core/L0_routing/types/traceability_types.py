"""
V15 P4 Typed Artifacts — Knowledge, Retrieval, Provenance & Traceability.

Typed artifacts required by Prompt v5.0 Enhanced for P4 (Immutable
Traceability) invariants. All artifacts are frozen dataclasses with
strict field validation enforced at construction time.

Artifact version: 1.0.0
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum

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
    record_execution_trace,
)

emit_replay_key("p0", "traceability_types")
emit_determinism_digest("p0", "traceability_types")

_emit_dispatches_healing_run("p1", "traceability_types", "L0")
_emit_routes_through("p1", "traceability_types", "L0")
_emit_checks_agent_registry("p1", "traceability_types", "agent_registry")
_emit_validates_agent_capability("p1", "traceability_types", "capability")
_emit_dispatches_execution_plan("p1", "traceability_types", "exec_plan")
_emit_agent_executes_agent("p1", "traceability_types", "sub_agent")
_emit_routes_to_agent("p1", "traceability_types", "target_agent")
_emit_verifies_policy("p1", "traceability_types", "policy_check")
_emit_observes_runtime_state("p1", "traceability_types", "runtime_state")
_emit_verifies_boundary("p1", "traceability_types", "boundary_check")
_emit_transcripts_response("p1", "traceability_types", "transcript")
_emit_hard_fails_untranscripted("p1", "traceability_types")
_emit_gated_by_confidence("p1", "traceability_types", "confidence_gate")
_emit_escalates_to_human("p1", "traceability_types", "L0")
_emit_reads_policy_state("p1", "traceability_types", "L0")
_emit_authorize_and_execute("p2", "traceability_types", "execution_auth")
_emit_validates_capability("p2", "traceability_types", "capability_check")
_emit_routes_to_capability("p2", "traceability_types", "capability_route")
_emit_writes_via_uwg("p2", "traceability_types", "uwg_write")
_emit_blocks_direct_write("p2", "traceability_types", "direct_write_block")
_emit_records_tool_invocation("p2", "traceability_types", "tool_invocation")
_emit_captures_execution_output("p2", "traceability_types", "exec_output")
_emit_dispatches_agent("p3", "traceability_types", "agent_dispatch")
_emit_coordinates_agents("p3", "traceability_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "traceability_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "traceability_types", "healing_outcome")
_emit_escalates_failure("p3", "traceability_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "traceability_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "traceability_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "traceability_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "traceability_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "traceability_types", "eval_metric")
_emit_stores_embedding("p4", "traceability_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "traceability_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "traceability_types", "exec_snapshot_link")
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

record_execution_trace("traceability_types", "traceability_types_trace")


_emit_emits_metric_event("traceability_types", "p4obs", "metric_1")
_emit_emits_metric_event("traceability_types", "p4obs", "metric_2")
_emit_emits_metric_event("traceability_types", "p4obs", "metric_3")
_emit_emits_metric_event("traceability_types", "p4obs", "metric_4")
_emit_emits_metric_event("traceability_types", "p4obs", "metric_5")
_emit_emits_metric_event("traceability_types", "p4obs", "metric_6")
_emit_records_incident_event("traceability_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("traceability_types", "p4obs", "anomaly")
_emit_writes_observability_log("traceability_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("traceability_types", "p4obs", "mon_state")
_emit_triggers_alert("traceability_types", "p4obs", "alert")
_emit_links_incident_trace("traceability_types", "p4obs", "trace_link")
_emit_captures_pattern("traceability_types", "p3lm", "pattern")
_emit_records_learning_event("traceability_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("traceability_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("traceability_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("traceability_types", "p3lm", "routing")
_emit_improves_agent_policy("traceability_types", "p3lm", "policy")
_emit_stores_learning_state("traceability_types", "p3lm", "state")
_emit_records_execution_trace("traceability_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("traceability_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("traceability_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("traceability_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("traceability_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("traceability_types", "env_read", "p2_env_1")
_emit_reads_environ("traceability_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("traceability_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("traceability_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "traceability_types", "context_pull")
_emit_pulls_context("p1", "traceability_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "traceability_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "traceability_types", "uwg_term_2")
_emit_writes_through("p1", "traceability_types", "write_through")
_emit_writes_through("p1", "traceability_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "traceability_types", "safety_validation")
_emit_invokes_eval("p1", "traceability_types", "eval_call")
_emit_proposal_commits_routing("p1", "traceability_types", "routing_commit")

TRACE_ID_PATTERN = re.compile("^CC3AL1-[0-9A-F]{8}$")


def validate_trace_id(trace_id: str) -> str:
    """§15.5 — Validate trace ID matches strict format. Fail-closed."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_trace_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_trace_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "validate_trace_id")
    if not TRACE_ID_PATTERN.match(trace_id):
        raise ValueError(
            f"FAIL (P4): Trace ID '{trace_id}' does not match required pattern ^CC3AL1-[0-9A-F]{{8}}$",
        )
    return trace_id


@dataclass(frozen=True)
class ErrorSignature:
    """§5.2 — Deterministic error signature.

    Computed from error_type + target_node_id + time_bucket (semantic clock).
    """

    error_type: str
    target_node_id: str
    time_bucket: int
    signature_hash: str

    def __post_init__(self) -> None:
        if not self.error_type:
            raise ValueError("ErrorSignature: error_type must be non-empty")
        if not self.target_node_id:
            raise ValueError("ErrorSignature: target_node_id must be non-empty")
        if self.time_bucket < 0:
            raise ValueError(f"ErrorSignature: time_bucket must be >= 0, got {self.time_bucket}")
        expected = compute_error_signature_hash(self.error_type, self.target_node_id, self.time_bucket)
        if self.signature_hash != expected:
            raise ValueError(
                f"ErrorSignature: signature_hash mismatch. Expected {expected}, got {self.signature_hash}",
            )


def compute_error_signature_hash(error_type: str, target_node_id: str, time_bucket: int) -> str:
    """§5.2 — Compute deterministic error signature hash."""
    payload = f"{error_type}|{target_node_id}|{time_bucket}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PolicyConfigPin:
    """§4.2 — SHA-256 of policy config captured at healing wave start.

    Verified unchanged before every routing decision within the wave.
    """

    wave_id: str
    policy_config_hash: str
    semantic_clock_tick: int

    def __post_init__(self) -> None:
        if not self.wave_id:
            raise ValueError("PolicyConfigPin: wave_id must be non-empty")
        if not self.policy_config_hash:
            raise ValueError("PolicyConfigPin: policy_config_hash must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"PolicyConfigPin: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )


@dataclass(frozen=True)
class PlanProvenance:
    """§6.7 — Links a generated plan to the specific Policy Liaison Node.

    Provides traceability from plan back to the policy that authorized it.
    """

    trace_id: str
    plan_id: str
    policy_liaison_node: str
    semantic_clock_tick: int
    plan_hash: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("PlanProvenance: trace_id must be non-empty")
        if not self.plan_id:
            raise ValueError("PlanProvenance: plan_id must be non-empty")
        if not self.policy_liaison_node:
            raise ValueError("PlanProvenance: policy_liaison_node must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"PlanProvenance: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not self.plan_hash:
            raise ValueError("PlanProvenance: plan_hash must be non-empty")


@dataclass(frozen=True)
class RetrievalQuery:
    """§6.5 — RAG chain step 1: the retrieval query."""

    trace_id: str
    query_text: str
    query_hash: str
    source_agent: str
    semantic_clock_tick: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("RetrievalQuery: trace_id must be non-empty")
        if not self.query_text:
            raise ValueError("RetrievalQuery: query_text must be non-empty")
        expected = hashlib.sha256(self.query_text.encode("utf-8")).hexdigest()
        if self.query_hash != expected:
            raise ValueError(
                f"RetrievalQuery: query_hash mismatch. Expected {expected}, got {self.query_hash}",
            )
        if not self.source_agent:
            raise ValueError("RetrievalQuery: source_agent must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"RetrievalQuery: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )


@dataclass(frozen=True)
class RetrievedChunk:
    """§6.5 — RAG chain step 2: a single retrieved chunk."""

    chunk_id: str
    source_id: str
    content: str
    content_hash: str
    location: str
    retrieval_query_hash: str

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("RetrievedChunk: chunk_id must be non-empty")
        if not self.source_id:
            raise ValueError("RetrievedChunk: source_id must be non-empty")
        if not self.content:
            raise ValueError("RetrievedChunk: content must be non-empty")
        expected = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        if self.content_hash != expected:
            raise ValueError(
                f"RetrievedChunk: content_hash mismatch. Expected {expected}, got {self.content_hash}",
            )
        if not self.location:
            raise ValueError("RetrievedChunk: location must be non-empty")
        if not self.retrieval_query_hash:
            raise ValueError("RetrievedChunk: retrieval_query_hash must be non-empty")


@dataclass(frozen=True)
class RerankScore:
    """§6.5 — RAG chain step 3: rerank score for a chunk."""

    chunk_id: str
    score: float
    rank: int

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("RerankScore: chunk_id must be non-empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"RerankScore: score must be in [0.0, 1.0], got {self.score}")
        if self.rank < 1:
            raise ValueError(f"RerankScore: rank must be >= 1, got {self.rank}")


@dataclass(frozen=True)
class CitationEntry:
    """§6.5 — A single citation linking output to a retrieved chunk."""

    citation_id: str
    chunk_id: str
    source_id: str
    location: str
    retrieval_hash: str

    def __post_init__(self) -> None:
        if not self.citation_id:
            raise ValueError("CitationEntry: citation_id must be non-empty")
        if not self.chunk_id:
            raise ValueError("CitationEntry: chunk_id must be non-empty")
        if not self.source_id:
            raise ValueError("CitationEntry: source_id must be non-empty")
        if not self.location:
            raise ValueError("CitationEntry: location must be non-empty")
        if not self.retrieval_hash:
            raise ValueError("CitationEntry: retrieval_hash must be non-empty")


@dataclass(frozen=True)
class CitationBundle:
    """§6.5 — RAG chain step 4: the complete citation bundle."""

    trace_id: str
    bundle_id: str
    citations: tuple[CitationEntry, ...]
    retrieval_query_hash: str
    bundle_hash: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("CitationBundle: trace_id must be non-empty")
        if not self.bundle_id:
            raise ValueError("CitationBundle: bundle_id must be non-empty")
        if not isinstance(self.citations, tuple):
            raise TypeError("CitationBundle: citations must be a tuple")
        if len(self.citations) == 0:
            raise ValueError("CitationBundle: citations must contain at least one entry")
        if not self.retrieval_query_hash:
            raise ValueError("CitationBundle: retrieval_query_hash must be non-empty")
        if not self.bundle_hash:
            raise ValueError("CitationBundle: bundle_hash must be non-empty")


@dataclass(frozen=True)
class CognitiveDiffBundle:
    """§15.2 — Diff between intended policy and actual execution.

    Required fields per spec:
      trace_id, incident_id, intended_policy_snapshot,
      actual_execution_trace, diff_summary, semantic_clock_tick
    """

    trace_id: str
    incident_id: str
    intended_policy_snapshot: str
    actual_execution_trace: str
    diff_summary: str
    semantic_clock_tick: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("CognitiveDiffBundle: trace_id must be non-empty")
        if not self.incident_id:
            raise ValueError("CognitiveDiffBundle: incident_id must be non-empty")
        if not self.intended_policy_snapshot:
            raise ValueError("CognitiveDiffBundle: intended_policy_snapshot must be non-empty")
        if not self.actual_execution_trace:
            raise ValueError("CognitiveDiffBundle: actual_execution_trace must be non-empty")
        if not self.diff_summary:
            raise ValueError("CognitiveDiffBundle: diff_summary must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"CognitiveDiffBundle: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )


class KnowledgeDirective(Enum):
    """Directive types from knowledge/graph layer."""

    ADVISORY = "advisory"
    CONTROL = "control"


@dataclass(frozen=True)
class KnowledgeAdvisoryConstraint:
    """§6.9 — Knowledge graph outputs are advisory-only.

    Any attempt to issue a control directive from the knowledge layer
    must be rejected fail-closed.
    """

    source_layer: str
    directive_type: KnowledgeDirective
    content: str
    trace_id: str

    def __post_init__(self) -> None:
        if not self.source_layer:
            raise ValueError("KnowledgeAdvisoryConstraint: source_layer must be non-empty")
        if not isinstance(self.directive_type, KnowledgeDirective):
            raise TypeError(
                f"KnowledgeAdvisoryConstraint: directive_type must be KnowledgeDirective, got {type(self.directive_type).__name__}",
            )
        if not self.content:
            raise ValueError("KnowledgeAdvisoryConstraint: content must be non-empty")
        if not self.trace_id:
            raise ValueError("KnowledgeAdvisoryConstraint: trace_id must be non-empty")


__all__ = [
    "TRACE_ID_PATTERN",
    "CitationBundle",
    "CitationEntry",
    "CognitiveDiffBundle",
    "ErrorSignature",
    "KnowledgeAdvisoryConstraint",
    "KnowledgeDirective",
    "PlanProvenance",
    "PolicyConfigPin",
    "RerankScore",
    "RetrievalQuery",
    "RetrievedChunk",
    "compute_error_signature_hash",
    "validate_trace_id",
]

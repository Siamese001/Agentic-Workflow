"""Trace feature types for the ADG-driven meta-learning bus.

Every execution trace is converted into a deterministic FeatureBundle
and stored as a TraceFeatureRecord linked to ADG node and relation IDs.
RCA clustering then groups these records into RCACluster objects that
drive optimization proposal generation.

Design invariants
-----------------
1. All types are frozen dataclasses — no mutation after construction.
2. No wall-clock reads; ``timestamp_utc`` is always caller-supplied.
3. stable_hash() = SHA-256(deterministic_json(to_dict())) for every type.
4. Influence class: C0_INFORMATIONAL — these records MUST NOT mutate
   routing, safety, or config state directly.
5. All tuple fields preserve insertion order; sort only where explicitly
   documented (e.g. adg_relation_ids for dedup stability).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Literal

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
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "trace_feature_types", "execution_auth")
_emit_validates_capability("p2", "trace_feature_types", "capability_check")
_emit_routes_to_capability("p2", "trace_feature_types", "capability_route")
_emit_writes_via_uwg("p2", "trace_feature_types", "uwg_write")
_emit_blocks_direct_write("p2", "trace_feature_types", "direct_write_block")
_emit_records_tool_invocation("p2", "trace_feature_types", "tool_invocation")
_emit_captures_execution_output("p2", "trace_feature_types", "exec_output")
_emit_dispatches_agent("p3", "trace_feature_types", "agent_dispatch")
_emit_coordinates_agents("p3", "trace_feature_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "trace_feature_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "trace_feature_types", "healing_outcome")
_emit_escalates_failure("p3", "trace_feature_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "trace_feature_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trace_feature_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "trace_feature_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "trace_feature_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trace_feature_types", "eval_metric")
_emit_stores_embedding("p4", "trace_feature_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "trace_feature_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trace_feature_types", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json

_emit_applies_guardrail("p0", "trace_feature_types", "p0_governance")
_emit_snapshots_state("p0", "trace_feature_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("trace_feature_types", "trace_feature_types_trace")


_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_1")
_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_2")
_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_3")
_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_4")
_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_5")
_emit_emits_metric_event("trace_feature_types", "p4obs", "metric_6")
_emit_records_incident_event("trace_feature_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("trace_feature_types", "p4obs", "anomaly")
_emit_writes_observability_log("trace_feature_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("trace_feature_types", "p4obs", "mon_state")
_emit_triggers_alert("trace_feature_types", "p4obs", "alert")
_emit_links_incident_trace("trace_feature_types", "p4obs", "trace_link")
_emit_captures_pattern("trace_feature_types", "p3lm", "pattern")
_emit_records_learning_event("trace_feature_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trace_feature_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("trace_feature_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trace_feature_types", "p3lm", "routing")
_emit_improves_agent_policy("trace_feature_types", "p3lm", "policy")
_emit_stores_learning_state("trace_feature_types", "p3lm", "state")
_emit_records_execution_trace("trace_feature_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trace_feature_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trace_feature_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trace_feature_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trace_feature_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trace_feature_types", "env_read", "p2_env_1")
_emit_reads_environ("trace_feature_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("trace_feature_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trace_feature_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trace_feature_types", "context_pull")
_emit_pulls_context("p1", "trace_feature_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trace_feature_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trace_feature_types", "uwg_term_2")
_emit_writes_through("p1", "trace_feature_types", "write_through")
_emit_writes_through("p1", "trace_feature_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "trace_feature_types", "safety_validation")
_emit_invokes_eval("p1", "trace_feature_types", "eval_call")
_emit_proposal_commits_routing("p1", "trace_feature_types", "routing_commit")
_emit_escalates_to_human("p1", "trace_feature_types", "human_escalation")
_emit_routes_through("p1", "trace_feature_types", "route_through")
_emit_checks_agent_registry("p1", "trace_feature_types", "agent_registry")
_emit_validates_agent_capability("p1", "trace_feature_types", "capability")
_emit_dispatches_execution_plan("p1", "trace_feature_types", "exec_plan")
_emit_agent_executes_agent("p1", "trace_feature_types", "sub_agent")
_emit_routes_to_agent("p1", "trace_feature_types", "target_agent")
_emit_verifies_policy("p1", "trace_feature_types", "policy_check")
_emit_observes_runtime_state("p1", "trace_feature_types", "runtime_state")
_emit_verifies_boundary("p1", "trace_feature_types", "boundary_check")
_emit_transcripts_response("p1", "trace_feature_types", "transcript")
_emit_hard_fails_untranscripted("p1", "trace_feature_types")
_emit_gated_by_confidence("p1", "trace_feature_types", "confidence_gate")
emit_replay_key("p0", "trace_feature_types")
emit_determinism_digest("p0", "trace_feature_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Outcome class literals
# ---------------------------------------------------------------------------

OutcomeClassLiteral = Literal[
    "SUCCESS",
    "SAFE_FAILURE",
    "HEALED_SUCCESS",
    "ROLLBACK",
    "HUMAN_OVERRIDE",
    "REPLAY_FAILURE",
    "UNKNOWN",
]

_VALID_OUTCOME_CLASSES: frozenset[str] = frozenset(
    {
        "SUCCESS",
        "SAFE_FAILURE",
        "HEALED_SUCCESS",
        "ROLLBACK",
        "HUMAN_OVERRIDE",
        "REPLAY_FAILURE",
        "UNKNOWN",
    },
)

# ---------------------------------------------------------------------------
# FeatureBundle — structured signal snapshot for one execution trace
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeatureBundle:
    """Structured feature snapshot extracted from a single execution trace.

    Each field maps directly to an ADG relation family.

    Attributes
    ----------
    trace_id : str
        Correlation ID of the originating execution trace.
    route_selected : str
        Routing path selected (e.g. ``"PATH_A"``, ``"PATH_D"``).
        Maps to ADG ``routes_path`` / ``routes_through``.
    confidence_gate_state : str
        State of the confidence gate at routing time
        (``"PASS"``, ``"STALL"``, ``"ESCALATE"``).
        Maps to ADG ``gated_by_confidence`` / ``forces_stall``.
    retrieval_path : str
        Retrieval strategy used (e.g. ``"RAG_BGE"``, ``"DIRECT"``,
        ``"SKIP"``).  Maps to ADG ``retrieves_via``.
    retrieval_groundedness_score : float
        Groundedness score from the retrieval step (0.0–1.0).
        Maps to ADG ``scores_groundedness``.
    policy_state_accessed : tuple[str, ...]
        Policy hashes accessed during this trace.
        Maps to ADG ``applies_policy``.
    guardrails_applied : tuple[str, ...]
        Guardrail IDs that fired during this trace.
        Maps to ADG ``applies_guardrail``.
    determinism_markers : tuple[str, ...]
        Replay keys or determinism digests present in this trace.
        Maps to ADG ``records_execution_trace``.
    healing_invoked : bool
        Whether a healer was invoked during this trace.
        Maps to ADG ``orchestrates_healing``.
    healer_id : str | None
        Healer identifier if healing was invoked.
        Maps to ADG ``dispatches_healing_run``.
    human_escalation_flag : bool
        Whether the trace was escalated to a human operator.
        Maps to ADG ``escalates_to_human``.
    mutation_presence : bool
        Whether any source mutation occurred during this trace.
        Maps to ADG ``records_mutation_transport``.
    final_outcome_class : str
        Outcome class of this trace (see ``_VALID_OUTCOME_CLASSES``).
    timestamp_utc : int
        Unix timestamp of the trace (caller-supplied, no wall-clock).
    adg_entity_name : str
        ADG entity name of the primary node associated with this trace.
    adg_relation_ids : tuple[str, ...]
        Sorted tuple of ADG relation IDs observed in this trace (for
        dedup stability across equivalent traces).
    influence_class : str
        Always ``"C0_INFORMATIONAL"`` — this bundle MUST NOT influence
        routing, safety, or config decisions directly.
    """

    trace_id: str
    route_selected: str
    confidence_gate_state: str
    retrieval_path: str
    retrieval_groundedness_score: float
    policy_state_accessed: tuple[str, ...]
    guardrails_applied: tuple[str, ...]
    determinism_markers: tuple[str, ...]
    healing_invoked: bool
    healer_id: str | None
    human_escalation_flag: bool
    mutation_presence: bool
    final_outcome_class: str
    timestamp_utc: int
    adg_entity_name: str
    adg_relation_ids: tuple[str, ...]
    routing_confidence: float = 0.0
    routing_target: str = ""
    influence_class: str = "C0_INFORMATIONAL"

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.final_outcome_class not in _VALID_OUTCOME_CLASSES:
            raise ValueError(
                f"final_outcome_class must be one of {sorted(_VALID_OUTCOME_CLASSES)}, "
                f"got {self.final_outcome_class!r}",
            )
        if not 0.0 <= self.retrieval_groundedness_score <= 1.0:
            raise ValueError(
                f"retrieval_groundedness_score must be in [0.0, 1.0], got {self.retrieval_groundedness_score}",
            )
        if not 0.0 <= self.routing_confidence <= 1.0:
            raise ValueError(f"routing_confidence must be in [0.0, 1.0], got {self.routing_confidence}")
        if self.influence_class != "C0_INFORMATIONAL":
            raise ValueError("influence_class must be C0_INFORMATIONAL")

    def _canonical_dict(self) -> dict:
        return {
            "adg_entity_name": self.adg_entity_name,
            "adg_relation_ids": sorted(self.adg_relation_ids),
            "confidence_gate_state": self.confidence_gate_state,
            "determinism_markers": list(self.determinism_markers),
            "final_outcome_class": self.final_outcome_class,
            "guardrails_applied": list(self.guardrails_applied),
            "healer_id": self.healer_id,
            "healing_invoked": self.healing_invoked,
            "human_escalation_flag": self.human_escalation_flag,
            "influence_class": self.influence_class,
            "mutation_presence": self.mutation_presence,
            "policy_state_accessed": list(self.policy_state_accessed),
            "retrieval_groundedness_score": round(self.retrieval_groundedness_score, 6),
            "retrieval_path": self.retrieval_path,
            "route_selected": self.route_selected,
            "routing_confidence": round(self.routing_confidence, 6),
            "routing_target": self.routing_target,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(deterministic_json(self._canonical_dict()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# TraceFeatureRecord — persisted record linking bundle to ADG
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TraceFeatureRecord:
    """Persisted learning record for a single execution trace.

    Links a FeatureBundle to ADG node and relation identifiers so that
    downstream clustering and proposal engines can query by ADG topology.

    Attributes
    ----------
    record_id : str
        Content-addressed ID = stable_hash() of this record.
    trace_id : str
        Originating trace correlation ID.
    route : str
        Route path selected.
    retrieval_pattern : str
        Retrieval strategy label.
    retrieval_groundedness : float
        Groundedness score (0.0–1.0).
    policy_edges : tuple[str, ...]
        Policy hash values observed.
    guardrail_edges : tuple[str, ...]
        Guardrail IDs fired.
    determinism_signals : tuple[str, ...]
        Replay / determinism markers.
    healer_used : str | None
        Healer identifier if healing was invoked.
    hitl_escalation : bool
        Whether HITL escalation occurred.
    outcome_class : str
        Final outcome class.
    adg_node_id : str
        Primary ADG entity name for this record.
    adg_relation_ids : tuple[str, ...]
        All ADG relation IDs observed (sorted for stability).
    feature_bundle_hash : str
        stable_hash() of the originating FeatureBundle.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    record_id: str
    trace_id: str
    route: str
    retrieval_pattern: str
    retrieval_groundedness: float
    policy_edges: tuple[str, ...]
    guardrail_edges: tuple[str, ...]
    determinism_signals: tuple[str, ...]
    healer_used: str | None
    hitl_escalation: bool
    outcome_class: str
    adg_node_id: str
    adg_relation_ids: tuple[str, ...]
    feature_bundle_hash: str
    timestamp_utc: int
    safety_audit_count: int = 0  # Count of safety audit records for this trace
    safety_audit_outcomes: tuple[str, ...] = ()  # Safety audit outcomes observed

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.outcome_class not in _VALID_OUTCOME_CLASSES:
            raise ValueError(
                f"outcome_class must be one of {sorted(_VALID_OUTCOME_CLASSES)}, got {self.outcome_class!r}",
            )

    def _canonical_dict(self) -> dict:
        return {
            "adg_node_id": self.adg_node_id,
            "adg_relation_ids": sorted(self.adg_relation_ids),
            "determinism_signals": list(self.determinism_signals),
            "feature_bundle_hash": self.feature_bundle_hash,
            "guardrail_edges": list(self.guardrail_edges),
            "healer_used": self.healer_used,
            "hitl_escalation": self.hitl_escalation,
            "outcome_class": self.outcome_class,
            "policy_edges": list(self.policy_edges),
            "record_id": self.record_id,
            "retrieval_groundedness": round(self.retrieval_groundedness, 6),
            "retrieval_pattern": self.retrieval_pattern,
            "route": self.route,
            "safety_audit_count": self.safety_audit_count,
            "safety_audit_outcomes": list(self.safety_audit_outcomes),
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(deterministic_json(self._canonical_dict()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())

    @staticmethod
    def from_bundle(bundle: FeatureBundle) -> TraceFeatureRecord:
        """Construct a TraceFeatureRecord from a FeatureBundle.

        record_id is set to the bundle's stable_hash so the ADG entity
        name for this record is deterministically derived from feature
        content.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TraceFeatureRecord.from_bundle")

        bundle_hash = bundle.stable_hash()
        # Build a temporary record to compute the stable record_id
        temp = TraceFeatureRecord(
            record_id=bundle_hash,
            trace_id=bundle.trace_id,
            route=bundle.route_selected,
            retrieval_pattern=bundle.retrieval_path,
            retrieval_groundedness=bundle.retrieval_groundedness_score,
            policy_edges=bundle.policy_state_accessed,
            guardrail_edges=bundle.guardrails_applied,
            determinism_signals=bundle.determinism_markers,
            healer_used=bundle.healer_id,
            hitl_escalation=bundle.human_escalation_flag,
            outcome_class=bundle.final_outcome_class,
            adg_node_id=bundle.adg_entity_name,
            adg_relation_ids=tuple(sorted(bundle.adg_relation_ids)),
            feature_bundle_hash=bundle_hash,
            timestamp_utc=bundle.timestamp_utc,
        )
        return temp


# ---------------------------------------------------------------------------
# RCACluster — ADG-keyed cluster of traces sharing a failure pattern
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RCACluster:
    """Cluster of traces sharing a dominant failure pattern.

    Produced by the RCA cluster engine from a set of TraceFeatureRecords.
    Feeds the optimization proposal generator.

    Attributes
    ----------
    cluster_id : str
        Content-addressed ID = stable_hash() of this cluster.
    failure_pattern : str
        Dominant failure category (e.g. ``"IMPORT_ERROR"``,
        ``"LOW_GROUNDEDNESS"``, ``"HEALER_TIMEOUT"``).
    dominant_route : str
        Most common route path in this cluster.
    dominant_guardrail : str | None
        Most common guardrail that fired (if any).
    dominant_retrieval_pattern : str
        Most common retrieval pattern in this cluster.
    affected_agents : tuple[str, ...]
        ADG entity names of affected agents / modules (sorted).
    member_trace_ids : tuple[str, ...]
        trace_ids of all member records (sorted for stability).
    member_count : int
        Number of member traces.
    outcome_distribution : tuple[tuple[str, int], ...]
        Sorted tuple of (outcome_class, count) pairs.
    avg_groundedness : float
        Mean retrieval groundedness score across members (rounded to 6dp).
    hitl_escalation_rate : float
        Fraction of members with HITL escalation (rounded to 6dp).
    healer_invocation_rate : float
        Fraction of members where a healer was invoked (rounded to 6dp).
    adg_cluster_node : str
        ADG entity name for this cluster (used by CaseLibrary / bridge).
    timestamp_utc : int
        Caller-supplied Unix timestamp of cluster creation.
    """

    cluster_id: str
    failure_pattern: str
    dominant_route: str
    dominant_guardrail: str | None
    dominant_retrieval_pattern: str
    affected_agents: tuple[str, ...]
    member_trace_ids: tuple[str, ...]
    member_count: int
    outcome_distribution: tuple[tuple[str, int], ...]
    avg_groundedness: float
    hitl_escalation_rate: float
    healer_invocation_rate: float
    adg_cluster_node: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.failure_pattern:
            raise ValueError("failure_pattern must not be empty")
        if self.member_count < 1:
            raise ValueError("member_count must be >= 1")

    def _canonical_dict(self) -> dict:
        return {
            "adg_cluster_node": self.adg_cluster_node,
            "affected_agents": sorted(self.affected_agents),
            "avg_groundedness": round(self.avg_groundedness, 6),
            "cluster_id": self.cluster_id,
            "dominant_guardrail": self.dominant_guardrail,
            "dominant_retrieval_pattern": self.dominant_retrieval_pattern,
            "dominant_route": self.dominant_route,
            "failure_pattern": self.failure_pattern,
            "healer_invocation_rate": round(self.healer_invocation_rate, 6),
            "hitl_escalation_rate": round(self.hitl_escalation_rate, 6),
            "member_count": self.member_count,
            "member_trace_ids": sorted(self.member_trace_ids),
            "outcome_distribution": sorted(self.outcome_distribution),
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(deterministic_json(self._canonical_dict()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# FailurePattern — negative case learning artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FailurePattern:
    """Negative-case learning artifact for a recurring failure signature.

    Sources: violates, antipattern, drift alerts, replay failures,
    low-groundedness retrieval, over-escalation.

    Attributes
    ----------
    pattern_id : str
        Content-addressed ID.
    source_type : str
        Category of negative signal (``"VIOLATION"``, ``"ANTIPATTERN"``,
        ``"DRIFT_ALERT"``, ``"REPLAY_FAILURE"``, ``"LOW_GROUNDEDNESS"``,
        ``"OVER_ESCALATION"``).
    signature : str
        Normalized failure signature string.
    affected_component : str
        ADG entity name of the affected component.
    occurrence_count : int
        Number of observed occurrences.
    evidence_hash : str
        SHA-256 of canonical evidence bytes.
    cluster_id : str | None
        Parent RCACluster if already grouped.
    timestamp_utc : int
        Caller-supplied timestamp.
    """

    pattern_id: str
    source_type: str
    signature: str
    affected_component: str
    occurrence_count: int
    evidence_hash: str
    cluster_id: str | None
    timestamp_utc: int

    _VALID_SOURCE_TYPES: frozenset[str] = field(
        default=frozenset(
            {
                "VIOLATION",
                "ANTIPATTERN",
                "DRIFT_ALERT",
                "REPLAY_FAILURE",
                "LOW_GROUNDEDNESS",
                "OVER_ESCALATION",
            },
        ),
        init=False,
        compare=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.source_type not in self._VALID_SOURCE_TYPES:
            raise ValueError(
                f"source_type must be one of {sorted(self._VALID_SOURCE_TYPES)}, got {self.source_type!r}",
            )
        if self.occurrence_count < 1:
            raise ValueError("occurrence_count must be >= 1")

    def _canonical_dict(self) -> dict:
        return {
            "affected_component": self.affected_component,
            "cluster_id": self.cluster_id,
            "evidence_hash": self.evidence_hash,
            "occurrence_count": self.occurrence_count,
            "pattern_id": self.pattern_id,
            "signature": self.signature,
            "source_type": self.source_type,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(deterministic_json(self._canonical_dict()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


__all__ = [
    "FailurePattern",
    "FeatureBundle",
    "OutcomeClassLiteral",
    "RCACluster",
    "TraceFeatureRecord",
]

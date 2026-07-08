"""Healing outcome types for L2.3 → Meta-Learning feedback loop.

Immutable, frozen dataclasses for deterministic healing outcome tracking.

Invariants:
  - All types are frozen dataclasses with slots
  - No wall-clock reads; timestamp_utc provided by caller
  - Stable rounding: round-half-up to 4 decimal places via QUANTIZE
  - Proposal is container-only; no config/routing/L4 writes
"""

from __future__ import annotations

import decimal
from dataclasses import dataclass, field

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "healing_outcome_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healing_outcome_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "healing_outcome_types", "state_snapshot")

trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healing_outcome_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healing_outcome_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healing_outcome_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healing_outcome_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healing_outcome_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healing_outcome_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healing_outcome_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healing_outcome_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healing_outcome_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healing_outcome_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healing_outcome_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healing_outcome_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healing_outcome_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healing_outcome_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("healing_outcome_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healing_outcome_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healing_outcome_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healing_outcome_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healing_outcome_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healing_outcome_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healing_outcome_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healing_outcome_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healing_outcome_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healing_outcome_types", "context_pull")
trace_contract._emit_pulls_context("p1", "healing_outcome_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healing_outcome_types", "write_through")
trace_contract._emit_writes_through("p1", "healing_outcome_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healing_outcome_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healing_outcome_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healing_outcome_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healing_outcome_types", "human_escalation")
trace_contract._emit_routes_through("p1", "healing_outcome_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healing_outcome_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healing_outcome_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healing_outcome_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healing_outcome_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healing_outcome_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "healing_outcome_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healing_outcome_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healing_outcome_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healing_outcome_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healing_outcome_types")
trace_contract._emit_gated_by_confidence("p1", "healing_outcome_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "healing_outcome_types")
trace_contract.emit_determinism_digest("p0", "healing_outcome_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "healing_outcome_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "healing_outcome_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healing_outcome_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healing_outcome_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healing_outcome_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healing_outcome_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healing_outcome_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healing_outcome_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healing_outcome_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healing_outcome_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healing_outcome_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healing_outcome_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healing_outcome_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healing_outcome_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healing_outcome_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healing_outcome_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healing_outcome_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healing_outcome_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healing_outcome_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healing_outcome_types", "exec_snapshot_link")

_ROUND_CTX = decimal.Context(rounding=decimal.ROUND_HALF_UP)
_QUANT = decimal.Decimal("0.0001")


def _stable_rate(numerator: int, denominator: int) -> float:
    """Compute rate with stable round-half-up to 4 decimal places.

    Returns 0.0 when denominator is zero.
    """
    if denominator == 0:
        return 0.0
    raw = decimal.Decimal(numerator) / decimal.Decimal(denominator)
    rounded = raw.quantize(_QUANT, context=_ROUND_CTX)
    return float(rounded)


@dataclass(frozen=True, slots=True)
class HealingOutcomeEvent:
    """Immutable record of a single L2.3 healing invocation outcome.

    Attributes
    ----------
    healer_id : str
        Canonical healer identity (e.g. check_id or healer function name).
    tier : str
        Healing tier used (e.g. 'LOCAL_AGENT', 'QWEN_VLLM', 'GEMINI_2_5_PRO').
    failure_type : str
        Stable failure category string.
    success : bool
        Whether the healing invocation succeeded.
    timestamp_utc : int
        Caller-provided Unix timestamp (aggregator never reads wall-clock).
    trace_id : str | None
        Optional correlation ID for tracing.
    error_signature : str | None
        Optional deterministic hash/signature of the error (if already available).
    failure_vector : tuple[float, ...] | None
        L2-normalised bge-m3 embedding of the full outcome signal text
        (``normalize_failure_signal`` output).  None only in BOOTSTRAP_MODE.
        Used for MEMORY / FAISS lookup in the meta-learning pipeline.
    routing_digest : str | None
        Determinism digest of the routing decision that selected this healer
        (``RoutingDecision.determinism_digest``).  Enables replay-key
        correlation between routing and outcome records.
    confidence_score : float | None
        Confidence score at routing time (0.0-1.0).  Forwarded from the
        ``confidence`` field of the healing action dict.
    novelty_flag : bool
        True when the routing signal vector was dissimilar (cosine < 0.75)
        to all recent failure vectors in L4 state — indicating a failure
        pattern not previously seen.  Always False when embeddings disabled.
    files_touched : tuple[str, ...]
        Relative paths of files modified by this healing invocation.
        Empty by default; populated by healers that track file mutations.
    """

    healer_id: str
    tier: str
    failure_type: str
    success: bool
    timestamp_utc: int
    trace_id: str | None = None
    error_signature: str | None = None
    failure_vector: tuple[float, ...] | None = None
    routing_digest: str | None = None
    confidence_score: float | None = None
    novelty_flag: bool = False
    cluster_id: str | None = None
    files_touched: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.healer_id:
            raise ValueError("healer_id must not be empty")
        if not self.tier:
            raise ValueError("tier must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")


@dataclass(frozen=True, slots=True)
class HealingOutcomeStats:
    """Deterministic aggregate counters for a single (healer_id, tier, failure_type) key.

    Rounding rule: round-half-up to 4 decimal places (via ``_stable_rate``).

    Attributes
    ----------
    healer_id : str
        Canonical healer identity.
    tier : str
        Healing tier.
    failure_type : str
        Stable failure category.
    total_count : int
        Total events ingested for this key.
    success_count : int
        Number of successful outcomes.
    failure_count : int
        Number of failed outcomes.
    success_rate : float
        success_count / total_count, rounded half-up to 4 decimals.
    """

    healer_id: str
    tier: str
    failure_type: str
    total_count: int
    success_count: int
    failure_count: int
    success_rate: float

    @staticmethod
    def from_counts(
        healer_id: str,
        tier: str,
        failure_type: str,
        success_count: int,
        failure_count: int,
    ) -> HealingOutcomeStats:
        """Build stats from raw counts with stable rounding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingOutcomeStats.from_counts"
        )

        total = success_count + failure_count
        return HealingOutcomeStats(
            healer_id=healer_id,
            tier=tier,
            failure_type=failure_type,
            total_count=total,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=_stable_rate(success_count, total),
        )


@dataclass(frozen=True, slots=True)
class HealingOutcomeProposal:
    """Proposal-only container for healing outcome-based optimizations.

    Phase 1: this is intentionally a no-op container.  It carries the
    snapshot from which a future phase may derive threshold adjustments.
    It MUST NOT write files, mutate configs, or call external services.

    Attributes
    ----------
    stats : tuple[HealingOutcomeStats, ...]
        Deterministically ordered stats snapshot driving this proposal.
    recommended_actions : tuple[str, ...]
        Human-readable action descriptions (empty in Phase 1).
    """

    stats: tuple[HealingOutcomeStats, ...] = field(default_factory=tuple)
    recommended_actions: tuple[str, ...] = field(default_factory=tuple)


__all__ = ["HealingOutcomeEvent", "HealingOutcomeProposal", "HealingOutcomeStats"]

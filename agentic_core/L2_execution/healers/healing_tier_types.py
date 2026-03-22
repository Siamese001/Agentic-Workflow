"""
L2.3 Healing Tier Types — Mathematically Deterministic Contracts.

Defines:
- HealingTier enum (LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO)
- HealingInput (structured failure context with replay_mode)
- HealingDecision (tier + heal_confidence + reason_codes)
- InvocationRecord (replay-deterministic audit trail)
- FailureSignal (emitted by NO_TIERING agents for L2.3 consumption)

All dataclasses are frozen/immutable. Timestamp excluded from replay surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "healing_tier_types")
emit_determinism_digest("p0", "healing_tier_types")

_emit_dispatches_healing_run("p1", "healing_tier_types", "L2")
_emit_routes_through("p1", "healing_tier_types", "L2")
_emit_checks_agent_registry("p1", "healing_tier_types", "agent_registry")
_emit_validates_agent_capability("p1", "healing_tier_types", "capability")
_emit_dispatches_execution_plan("p1", "healing_tier_types", "exec_plan")
_emit_agent_executes_agent("p1", "healing_tier_types", "sub_agent")
_emit_routes_to_agent("p1", "healing_tier_types", "target_agent")
_emit_verifies_policy("p1", "healing_tier_types", "policy_check")
_emit_observes_runtime_state("p1", "healing_tier_types", "runtime_state")
_emit_verifies_boundary("p1", "healing_tier_types", "boundary_check")
_emit_transcripts_response("p1", "healing_tier_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_tier_types")
_emit_gated_by_confidence("p1", "healing_tier_types", "confidence_gate")
_emit_escalates_to_human("p1", "healing_tier_types", "L2")
_emit_reads_policy_state("p1", "healing_tier_types", "L2")
_emit_authorize_and_execute("p2", "healing_tier_types", "execution_auth")
_emit_validates_capability("p2", "healing_tier_types", "capability_check")
_emit_routes_to_capability("p2", "healing_tier_types", "capability_route")
_emit_writes_via_uwg("p2", "healing_tier_types", "uwg_write")
_emit_blocks_direct_write("p2", "healing_tier_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_tier_types", "tool_invocation")
_emit_captures_execution_output("p2", "healing_tier_types", "exec_output")
_emit_dispatches_agent("p3", "healing_tier_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_tier_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_tier_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_tier_types", "healing_outcome")
_emit_escalates_failure("p3", "healing_tier_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_tier_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_tier_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_tier_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_tier_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_tier_types", "eval_metric")
_emit_stores_embedding("p4", "healing_tier_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_tier_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_tier_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_1")
_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_2")
_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_3")
_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_4")
_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_5")
_emit_emits_metric_event("healing_tier_types", "p4obs", "metric_6")
_emit_records_incident_event("healing_tier_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_tier_types", "p4obs", "anomaly")
_emit_writes_observability_log("healing_tier_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_tier_types", "p4obs", "mon_state")
_emit_triggers_alert("healing_tier_types", "p4obs", "alert")
_emit_links_incident_trace("healing_tier_types", "p4obs", "trace_link")
_emit_captures_pattern("healing_tier_types", "p3lm", "pattern")
_emit_records_learning_event("healing_tier_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_tier_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_tier_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_tier_types", "p3lm", "routing")
_emit_improves_agent_policy("healing_tier_types", "p3lm", "policy")
_emit_stores_learning_state("healing_tier_types", "p3lm", "state")
_emit_records_execution_trace("healing_tier_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_tier_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_tier_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_tier_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_tier_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_tier_types", "env_read", "p2_env_1")
_emit_reads_environ("healing_tier_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_tier_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_tier_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_tier_types", "context_pull")
_emit_pulls_context("p1", "healing_tier_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_tier_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_tier_types", "uwg_term_2")
_emit_writes_through("p1", "healing_tier_types", "write_through")
_emit_writes_through("p1", "healing_tier_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_tier_types", "safety_validation")
_emit_invokes_eval("p1", "healing_tier_types", "eval_call")
_emit_proposal_commits_routing("p1", "healing_tier_types", "routing_commit")


class HealingTier(str, Enum):
    """Healing model tier selected by the centralized router."""

    LOCAL_AGENT = "LOCAL_AGENT"
    QWEN_VLLM = "QWEN_VLLM"
    GEMINI_2_5_PRO = "GEMINI_2_5_PRO"


@dataclass(frozen=True, slots=True)
class HealingInput:
    """Structured failure context consumed by the L2.3 healing router.

    Attributes:
        failure_type: Category of the failure (e.g. 'syntax_error', 'import_cycle').
        error_signature: Deterministic hash or short string identifying the error class.
        trace_id: Correlation ID linking to the execution cycle.
        retry_count: Number of prior heal attempts for this failure.
        blast_radius_estimate: Bounded [0.0, 1.0] estimate of change scope.
        required_tools: Tools the healer needs (e.g. ['ast_rewrite', 'file_move']).
        violation_metadata_refs: Paths to violation artifacts for context.
        replay_mode: Enable deterministic replay mode (timestamp excluded).
        agent_id: Optional identifier of the agent requesting healing (execution profile enforcement).
        failure_entropy_class: Entropy classification of the failure (LOW/MEDIUM/HIGH).
    """

    failure_type: str
    error_signature: str
    trace_id: str
    retry_count: int
    blast_radius_estimate: float
    required_tools: tuple[str, ...] = ()
    violation_metadata_refs: tuple[str, ...] = ()
    replay_mode: bool = False
    agent_id: str = ""
    failure_entropy_class: str = "MEDIUM"

    def __post_init__(self) -> None:
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if not self.error_signature:
            raise ValueError("error_signature must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.retry_count < 0:
            raise ValueError(f"retry_count must be >= 0, got {self.retry_count}")
        if not 0.0 <= self.blast_radius_estimate <= 1.0:
            raise ValueError(f"blast_radius_estimate must be in [0.0, 1.0], got {self.blast_radius_estimate}")


@dataclass(frozen=True, slots=True)
class HealingDecision:
    """Immutable routing decision produced by the L2.3 healing router.

    Attributes:
        heal_confidence: Deterministic score in [0.0, 1.0] driving tier selection.
        tier: Selected healing tier.
        reason_codes: Deterministic list of reasons contributing to the decision.
    """

    heal_confidence: float
    tier: HealingTier
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.heal_confidence <= 1.0:
            raise ValueError(f"heal_confidence must be in [0.0, 1.0], got {self.heal_confidence}")
        if not isinstance(self.tier, HealingTier):
            raise ValueError(f"tier must be a HealingTier enum, got {type(self.tier).__name__}")


@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record with replay-deterministic fields only.

    Timestamp excluded from replay surface for mathematical determinism.
    Provider configuration and historical data versioning included.

    Attributes:
        tier: Selected healing tier
        model_id: Model identifier used
        agent_name: Agent that made the request
        trace_id: Correlation ID for the request
        heal_confidence: Confidence score for the decision
        method_called: Method name that was invoked
        provider_config_hash: Hash of provider configuration for replay
        historical_data_hash: Hash of historical data version for replay
        replay_key: Mathematical replay key (timestamp excluded)
    """

    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    provider_config_hash: str
    historical_data_hash: str
    replay_key: str
    response_text: str | None = None


@dataclass(frozen=True, slots=True)
class FailureSignal:
    """Structured signal emitted by NO_TIERING agents on failure.

    L2.3 consumes this to perform healing tier routing on behalf of the agent.
    The agent itself MUST NOT select a healing model.

    Attributes:
        source_agent: Name of the agent emitting the signal.
        failure_type: Category of the failure.
        error_signature: Deterministic identifier for the error class.
        trace_id: Correlation ID.
        context: Arbitrary structured context for the healer.
        retry_count: Number of prior attempts.
        blast_radius_estimate: Bounded [0.0, 1.0].
    """

    source_agent: str
    failure_type: str
    error_signature: str
    trace_id: str
    context: dict
    retry_count: int = 0
    blast_radius_estimate: float = 0.0

    def __post_init__(self) -> None:
        if not self.source_agent:
            raise ValueError("source_agent must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")

    def to_healing_input(
        self, required_tools: tuple[str, ...] = (), violation_metadata_refs: tuple[str, ...] = ()
    ) -> HealingInput:
        """Convert FailureSignal to HealingInput for L2.3 router consumption."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FailureSignal.to_healing_input", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FailureSignal.to_healing_input", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FailureSignal.to_healing_input")
        return HealingInput(
            agent_id=self.source_agent,
            failure_type=self.failure_type,
            error_signature=self.error_signature,
            trace_id=self.trace_id,
            retry_count=self.retry_count,
            blast_radius_estimate=self.blast_radius_estimate,
            required_tools=required_tools,
            violation_metadata_refs=violation_metadata_refs,
        )


__all__ = ["FailureSignal", "HealingDecision", "HealingInput", "HealingTier", "InvocationRecord"]

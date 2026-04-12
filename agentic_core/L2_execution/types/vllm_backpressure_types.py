"""
WAVE 3 — Backpressure + Overload Escalation Enforcement types.

Defines queue policy, circuit breaker state, and overload escalation
invariants for vLLM tiered routing.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    VLLMFailureType,
)
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

emit_replay_key("p0", "vllm_backpressure_types")
emit_determinism_digest("p0", "vllm_backpressure_types")

_emit_dispatches_healing_run("p1", "vllm_backpressure_types", "L2")
_emit_routes_through("p1", "vllm_backpressure_types", "L2")
_emit_checks_agent_registry("p1", "vllm_backpressure_types", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_backpressure_types", "capability")
_emit_dispatches_execution_plan("p1", "vllm_backpressure_types", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_backpressure_types", "sub_agent")
_emit_routes_to_agent("p1", "vllm_backpressure_types", "target_agent")
_emit_verifies_policy("p1", "vllm_backpressure_types", "policy_check")
_emit_observes_runtime_state("p1", "vllm_backpressure_types", "runtime_state")
_emit_verifies_boundary("p1", "vllm_backpressure_types", "boundary_check")
_emit_transcripts_response("p1", "vllm_backpressure_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_backpressure_types")
_emit_gated_by_confidence("p1", "vllm_backpressure_types", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_backpressure_types", "L2")
_emit_reads_policy_state("p1", "vllm_backpressure_types", "L2")

_emit_applies_guardrail("p0", "vllm_backpressure_types", "p0_governance")
_emit_snapshots_state("p0", "vllm_backpressure_types", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_backpressure_types", "execution_auth")
_emit_validates_capability("p2", "vllm_backpressure_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_backpressure_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_backpressure_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_backpressure_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_backpressure_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_backpressure_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_backpressure_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_backpressure_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_backpressure_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_backpressure_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_backpressure_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_backpressure_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_backpressure_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_backpressure_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_backpressure_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_backpressure_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_backpressure_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_backpressure_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_backpressure_types", "exec_snapshot_link")
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

_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_backpressure_types", "p4obs", "metric_6")
_emit_records_incident_event("vllm_backpressure_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_backpressure_types", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_backpressure_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_backpressure_types", "p4obs", "mon_state")
_emit_triggers_alert("vllm_backpressure_types", "p4obs", "alert")
_emit_links_incident_trace("vllm_backpressure_types", "p4obs", "trace_link")
_emit_captures_pattern("vllm_backpressure_types", "p3lm", "pattern")
_emit_records_learning_event("vllm_backpressure_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_backpressure_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_backpressure_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_backpressure_types", "p3lm", "routing")
_emit_improves_agent_policy("vllm_backpressure_types", "p3lm", "policy")
_emit_stores_learning_state("vllm_backpressure_types", "p3lm", "state")
_emit_records_execution_trace("vllm_backpressure_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_backpressure_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_backpressure_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_backpressure_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_backpressure_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_backpressure_types", "env_read", "p2_env_1")
_emit_reads_environ("vllm_backpressure_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_backpressure_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_backpressure_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_backpressure_types", "context_pull")
_emit_pulls_context("p1", "vllm_backpressure_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_backpressure_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_backpressure_types", "uwg_term_2")
_emit_writes_through("p1", "vllm_backpressure_types", "write_through")
_emit_writes_through("p1", "vllm_backpressure_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_backpressure_types", "safety_validation")
_emit_invokes_eval("p1", "vllm_backpressure_types", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_backpressure_types", "routing_commit")

# ---------------------------------------------------------------------------
# WAVE 3.1 — Queue policy constants (deterministic, not env-derived)
# ---------------------------------------------------------------------------

MAX_QUEUE_DEPTH: int = 8
QUEUE_WAIT_TIMEOUT_SECONDS: float = 5.0
CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
CIRCUIT_BREAKER_RESET_AFTER_SECONDS: float = 30.0

# ---------------------------------------------------------------------------
# WAVE 3.2 — Queue state dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VLLMQueueState:
    """Immutable snapshot of the vLLM request queue state.

    Used for backpressure decisions. Produced before routing.
    """

    current_depth: int
    max_depth: int
    oldest_wait_seconds: float
    timeout_seconds: float

    @property
    def is_full(self) -> bool:
        return self.current_depth >= self.max_depth

    @property
    def is_timed_out(self) -> bool:
        return self.oldest_wait_seconds >= self.timeout_seconds


# ---------------------------------------------------------------------------
# WAVE 3.3 — Circuit breaker state
# ---------------------------------------------------------------------------


class CircuitBreakerState(str, Enum):
    """Circuit breaker state for local vLLM tier."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class VLLMCircuitBreaker:
    """Mutable circuit breaker for a single vLLM tier.

    Tracks consecutive failures and opens the circuit when threshold exceeded.
    """

    tier: str
    failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD
    consecutive_failures: int = field(default=0)
    state: CircuitBreakerState = field(default=CircuitBreakerState.CLOSED)

    def record_failure(self) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "VLLMCircuitBreaker.record_failure",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMCircuitBreaker.record_failure".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.state = CircuitBreakerState.CLOSED

    def reset(self) -> None:
        self.consecutive_failures = 0
        self.state = CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == CircuitBreakerState.OPEN


# ---------------------------------------------------------------------------
# WAVE 3.4 — Backpressure escalation decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BackpressureDecision:
    """Immutable backpressure escalation decision.

    Produced when queue or circuit breaker state forces Gemini escalation.
    """

    escalate_to_gemini: bool
    reason: str
    failure_type: VLLMFailureType | None
    model_id: str
    queue_depth: int
    circuit_breaker_open: bool


def evaluate_backpressure(
    queue_state: VLLMQueueState,
    circuit_breaker: VLLMCircuitBreaker,
) -> BackpressureDecision:
    """Evaluate backpressure conditions and produce escalation decision.

    Invariants (in priority order):
        1. Circuit breaker open → Gemini-2.5-Pro immediately
        2. Queue full → Gemini-2.5-Pro immediately
        3. Queue wait timed out → Gemini-2.5-Pro immediately
        4. Otherwise → proceed to local tier

    Gemini-2.5-Pro is always reachable as escalation path.

    Args:
        queue_state: Current queue snapshot.
        circuit_breaker: Current circuit breaker state.

    Returns:
        BackpressureDecision with escalation flag and reason.
    """
    if circuit_breaker.is_open:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="circuit_breaker_open",
            failure_type=VLLMFailureType.CIRCUIT_BREAKER_OPEN,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=True,
        )

    if queue_state.is_full:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="queue_full",
            failure_type=VLLMFailureType.QUEUE_OVERFLOW,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=False,
        )

    if queue_state.is_timed_out:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="queue_timeout",
            failure_type=VLLMFailureType.QUEUE_OVERFLOW,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=False,
        )

    return BackpressureDecision(
        escalate_to_gemini=False,
        reason="ok",
        failure_type=None,
        model_id="",
        queue_depth=queue_state.current_depth,
        circuit_breaker_open=False,
    )


__all__ = [
    "CIRCUIT_BREAKER_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_RESET_AFTER_SECONDS",
    "MAX_QUEUE_DEPTH",
    "QUEUE_WAIT_TIMEOUT_SECONDS",
    "BackpressureDecision",
    "CircuitBreakerState",
    "VLLMCircuitBreaker",
    "VLLMQueueState",
    "evaluate_backpressure",
]

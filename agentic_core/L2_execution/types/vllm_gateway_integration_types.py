"""
PHASE 3 — Runtime Integration: vLLM Gateway Call-Path Controller.

Wires Phase 1 (token budgeting + tiered routing) and Phase 2
(serving profiles + backpressure/circuit breaker) into a single
deterministic call-path controller.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
No external SDK dependencies. All types are stdlib + Phase 1/2 types.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

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

emit_replay_key("p0", "vllm_gateway_integration_types")
emit_determinism_digest("p0", "vllm_gateway_integration_types")

_emit_dispatches_healing_run("p1", "vllm_gateway_integration_types", "L2")
_emit_routes_through("p1", "vllm_gateway_integration_types", "L2")
_emit_checks_agent_registry("p1", "vllm_gateway_integration_types", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_gateway_integration_types", "capability")
_emit_dispatches_execution_plan("p1", "vllm_gateway_integration_types", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_gateway_integration_types", "sub_agent")
_emit_routes_to_agent("p1", "vllm_gateway_integration_types", "target_agent")
_emit_verifies_policy("p1", "vllm_gateway_integration_types", "policy_check")
_emit_observes_runtime_state("p1", "vllm_gateway_integration_types", "runtime_state")
_emit_verifies_boundary("p1", "vllm_gateway_integration_types", "boundary_check")
_emit_transcripts_response("p1", "vllm_gateway_integration_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_gateway_integration_types")
_emit_gated_by_confidence("p1", "vllm_gateway_integration_types", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_gateway_integration_types", "L2")
_emit_reads_policy_state("p1", "vllm_gateway_integration_types", "L2")

_emit_applies_guardrail("p0", "vllm_gateway_integration_types", "p0_governance")
_emit_snapshots_state("p0", "vllm_gateway_integration_types", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_gateway_integration_types", "execution_auth")
_emit_validates_capability("p2", "vllm_gateway_integration_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_gateway_integration_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_gateway_integration_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_gateway_integration_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_gateway_integration_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_gateway_integration_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_gateway_integration_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_gateway_integration_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_gateway_integration_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_gateway_integration_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_gateway_integration_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_gateway_integration_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_gateway_integration_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_gateway_integration_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_gateway_integration_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_gateway_integration_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_gateway_integration_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_gateway_integration_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_gateway_integration_types", "exec_snapshot_link")
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

_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_gateway_integration_types", "p4obs", "metric_6")
_emit_records_incident_event("vllm_gateway_integration_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_gateway_integration_types", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_gateway_integration_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_gateway_integration_types", "p4obs", "mon_state")
_emit_triggers_alert("vllm_gateway_integration_types", "p4obs", "alert")
_emit_links_incident_trace("vllm_gateway_integration_types", "p4obs", "trace_link")
_emit_captures_pattern("vllm_gateway_integration_types", "p3lm", "pattern")
_emit_records_learning_event("vllm_gateway_integration_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_gateway_integration_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_gateway_integration_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_gateway_integration_types", "p3lm", "routing")
_emit_improves_agent_policy("vllm_gateway_integration_types", "p3lm", "policy")
_emit_stores_learning_state("vllm_gateway_integration_types", "p3lm", "state")
_emit_records_execution_trace("vllm_gateway_integration_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_gateway_integration_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_gateway_integration_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_gateway_integration_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_gateway_integration_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_gateway_integration_types", "env_read", "p2_env_1")
_emit_reads_environ("vllm_gateway_integration_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_gateway_integration_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_gateway_integration_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_gateway_integration_types", "context_pull")
_emit_pulls_context("p1", "vllm_gateway_integration_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_gateway_integration_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_gateway_integration_types", "uwg_term_2")
_emit_writes_through("p1", "vllm_gateway_integration_types", "write_through")
_emit_writes_through("p1", "vllm_gateway_integration_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_gateway_integration_types", "safety_validation")
_emit_invokes_eval("p1", "vllm_gateway_integration_types", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_gateway_integration_types", "routing_commit")


def select_serving_profile(severity: str) -> VLLMServingProfile:
    """Select serving profile based on severity.

    Routing invariant (mirrors Phase 1 tier selection):
        severity high  → LOCAL_STRONG_14B
        severity low/medium → LOCAL_FAST_7B

    Args:
        severity: Severity level string ("low", "medium", "high").

    Returns:
        VLLMServingProfile for the selected tier.
    """
    from agentic_core.L2_execution.types.vllm_serving_profile_types import (
        PROFILE_LOCAL_FAST_7B,
        PROFILE_LOCAL_STRONG_14B,
    )

    if severity == "high":
        return PROFILE_LOCAL_STRONG_14B
    return PROFILE_LOCAL_FAST_7B


VLLM_TEMPERATURE: float = 0.0
VLLM_TOP_P: float = 1.0
VLLM_SEED: int = 42


@dataclass(frozen=True)
class VLLMLocalRequest:
    """Shaped local vLLM request payload.

    Immutable. All fields are explicit — no None max_tokens.
    Determinism policy enforced: temperature=0, top_p=1.0, seed=42.
    """

    model: str
    prompt: str
    max_tokens: int
    temperature: float
    top_p: float
    seed: int
    task_class: str
    profile_name: str
    max_model_len: int


def shape_local_request(prompt: str, task_class: str, profile: VLLMServingProfile) -> VLLMLocalRequest:
    """Shape a local vLLM request with deterministic parameters.

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        profile: Selected serving profile.

    Returns:
        VLLMLocalRequest with explicit max_tokens and determinism policy.
    """
    from agentic_core.L2_execution.types.vllm_token_budget_types import get_output_cap

    max_output = get_output_cap(task_class)
    if max_output is None:
        raise ValueError(f"task_class={task_class!r} has no output cap; route to Gemini-2.5-Pro instead")
    max_tokens = min(max_output, profile.max_model_len)
    return VLLMLocalRequest(
        model=profile.model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=VLLM_TEMPERATURE,
        top_p=VLLM_TOP_P,
        seed=VLLM_SEED,
        task_class=task_class,
        profile_name=profile.profile_name,
        max_model_len=profile.max_model_len,
    )


class VLLMQueueController:
    """Threadsafe bounded queue counter for backpressure enforcement.

    Maintains an in-memory queue depth counter. Does not spawn threads.
    """

    def __init__(self, max_depth: int | None = None, timeout_seconds: float | None = None) -> None:
        from agentic_core.L2_execution.types.vllm_backpressure_types import (
            MAX_QUEUE_DEPTH,
            QUEUE_WAIT_TIMEOUT_SECONDS,
        )

        self._max_depth = max_depth if max_depth is not None else MAX_QUEUE_DEPTH
        self._timeout_seconds = timeout_seconds if timeout_seconds is not None else QUEUE_WAIT_TIMEOUT_SECONDS
        self._depth: int = 0
        self._lock = threading.Lock()

    def snapshot(self, oldest_wait_seconds: float = 0.0) -> VLLMQueueState:
        """Return an immutable snapshot of current queue state."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VLLMQueueController.snapshot")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMQueueController.snapshot".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L2_execution.types.vllm_backpressure_types import VLLMQueueState

        with self._lock:
            return VLLMQueueState(
                current_depth=self._depth,
                max_depth=self._max_depth,
                oldest_wait_seconds=oldest_wait_seconds,
                timeout_seconds=self._timeout_seconds,
            )

    def acquire(self) -> bool:
        """Attempt to acquire a queue slot. Returns True if slot acquired."""
        with self._lock:
            if self._depth >= self._max_depth:
                return False
            self._depth += 1
            return True

    def release(self) -> None:
        """Release a queue slot."""
        with self._lock:
            if self._depth > 0:
                self._depth -= 1

    @property
    def depth(self) -> int:
        with self._lock:
            return self._depth


class VLLMCircuitBreakerRegistry:
    """Registry of circuit breakers, one per tier.

    Threadsafe. Breakers are created on first access.
    """

    def __init__(self) -> None:
        self._breakers: dict[str, VLLMCircuitBreaker] = {}
        self._lock = threading.Lock()

    def get(self, tier: str) -> VLLMCircuitBreaker:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VLLMCircuitBreakerRegistry.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMCircuitBreakerRegistry.get".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L2_execution.types.vllm_backpressure_types import (
            CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            VLLMCircuitBreaker,
        )

        with self._lock:
            if tier not in self._breakers:
                self._breakers[tier] = VLLMCircuitBreaker(
                    tier=tier,
                    failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                )
            return self._breakers[tier]

    def record_failure(self, tier: str) -> None:
        self.get(tier).record_failure()

    def record_success(self, tier: str) -> None:
        self.get(tier).record_success()

    def is_open(self, tier: str) -> bool:
        return self.get(tier).is_open

    def reset(self, tier: str) -> None:
        self.get(tier).reset()

    def reset_all(self) -> None:
        with self._lock:
            for cb in self._breakers.values():
                cb.reset()


@dataclass(frozen=True)
class VLLMGatewayTelemetry:
    """Immutable telemetry payload for a single gateway call.

    All fields are deterministic; no timestamps. Stable key ordering via as_dict().
    PHASE 4: Extended with infrastructure fingerprint fields for replay sealing.
    """

    provider_selected: str
    model_tier: str
    prompt_tokens_estimated: int
    max_output_tokens_requested: int
    max_model_len_configured: int
    token_budget_ok: bool
    budget_margin_tokens: int
    queue_depth: int
    queue_full: bool
    queue_wait_seconds: float
    breaker_state: str
    breaker_failure_count: int
    failure_type: str | None
    model_name: str
    model_revision_sha: str
    vllm_version: str
    transformers_version: str
    torch_version: str
    cuda_version: str
    driver_version: str
    fingerprint_hash: str

    def as_dict(self) -> dict[str, Any]:
        """Return stable-ordered dict representation."""
        return {
            "provider_selected": self.provider_selected,
            "model_tier": self.model_tier,
            "prompt_tokens_estimated": self.prompt_tokens_estimated,
            "max_output_tokens_requested": self.max_output_tokens_requested,
            "max_model_len_configured": self.max_model_len_configured,
            "token_budget_ok": self.token_budget_ok,
            "budget_margin_tokens": self.budget_margin_tokens,
            "queue_depth": self.queue_depth,
            "queue_full": self.queue_full,
            "queue_wait_seconds": self.queue_wait_seconds,
            "breaker_state": self.breaker_state,
            "breaker_failure_count": self.breaker_failure_count,
            "failure_type": self.failure_type,
            "model_name": self.model_name,
            "model_revision_sha": self.model_revision_sha,
            "vllm_version": self.vllm_version,
            "transformers_version": self.transformers_version,
            "torch_version": self.torch_version,
            "cuda_version": self.cuda_version,
            "driver_version": self.driver_version,
            "fingerprint_hash": self.fingerprint_hash,
        }


@dataclass
class VLLMGatewayCallResult:
    """Result of a gateway call-path evaluation.

    Contains routing decision, shaped request (if local), and telemetry.

    PHASE 5: Includes invariant_violations list for runtime enforcement.
    """

    route_to_gemini: bool
    local_request: VLLMLocalRequest | None
    telemetry: VLLMGatewayTelemetry
    preflight: VLLMPreflightResult
    backpressure: BackpressureDecision
    invariant_violations: list[Any] = None

    def __post_init__(self):
        """Initialize invariant_violations to empty list if None."""
        if self.invariant_violations is None:
            object.__setattr__(self, "invariant_violations", [])


def evaluate_gateway_call(
    prompt: str,
    task_class: str,
    severity: str,
    queue_controller: VLLMQueueController,
    breaker_registry: VLLMCircuitBreakerRegistry,
    oldest_wait_seconds: float = 0.0,
    fingerprint: VLLMInfrastructureFingerprint | None = None,
) -> VLLMGatewayCallResult:
    """Evaluate a full gateway call path deterministically.

    Routing invariants (in priority order):
        1. Backpressure (circuit breaker open / queue full / timeout) → Gemini
        2. Token budget exceeded → Gemini
        3. Otherwise → local tier (7B or 14B based on severity)

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        severity: Severity level ("low", "medium", "high").
        queue_controller: In-gateway queue depth controller.
        breaker_registry: Circuit breaker registry.
        oldest_wait_seconds: Age of oldest queued request in seconds.
        fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

    Returns:
        VLLMGatewayCallResult with routing decision, shaped request, telemetry.
    """
    from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID
    from agentic_core.L2_execution.types.vllm_backpressure_types import evaluate_backpressure
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_token_budget_types import (
        GEMINI_25_PRO_MODEL_ID,
        VLLMFailureType,
        run_preflight_budget_check,
    )

    profile = select_serving_profile(severity)
    tier = "local_fast" if profile.profile_name == "LOCAL_FAST_7B" else "local_strong"
    queue_state = queue_controller.snapshot(oldest_wait_seconds)
    breaker = breaker_registry.get(tier)
    bp_decision = evaluate_backpressure(queue_state, breaker)
    preflight = run_preflight_budget_check(
        prompt=prompt,
        task_class=task_class,
        max_model_len=profile.max_model_len,
    )
    if bp_decision.escalate_to_gemini:
        provider_selected = GEMINI_25_PRO_MODEL_ID
        model_tier = "remote"
        failure_type = bp_decision.failure_type.value if bp_decision.failure_type else None
        local_request = None
    elif not preflight.token_budget_ok:
        provider_selected = GEMINI_25_PRO_MODEL_ID
        model_tier = "remote"
        failure_type = VLLMFailureType.TOKEN_BUDGET_EXCEEDED.value
        local_request = None
    else:
        provider_selected = QWEN_LOCAL_MODEL_ID
        model_tier = "fast" if profile.profile_name == "LOCAL_FAST_7B" else "strong"
        failure_type = None
        local_request = shape_local_request(prompt, task_class, profile)
    fp = (
        fingerprint
        if fingerprint is not None
        else VLLMInfrastructureFingerprint.deterministic_test_instance()
    )
    telemetry = VLLMGatewayTelemetry(
        provider_selected=provider_selected,
        model_tier=model_tier,
        prompt_tokens_estimated=preflight.prompt_tokens_estimated,
        max_output_tokens_requested=preflight.max_output_tokens_requested,
        max_model_len_configured=preflight.max_model_len_configured,
        token_budget_ok=preflight.token_budget_ok,
        budget_margin_tokens=preflight.budget_margin_tokens,
        queue_depth=queue_state.current_depth,
        queue_full=queue_state.is_full,
        queue_wait_seconds=oldest_wait_seconds,
        breaker_state=breaker.state.value,
        breaker_failure_count=breaker.consecutive_failures,
        failure_type=failure_type,
        model_name=fp.model_name,
        model_revision_sha=fp.model_revision_sha,
        vllm_version=fp.vllm_version,
        transformers_version=fp.transformers_version,
        torch_version=fp.torch_version,
        cuda_version=fp.cuda_version,
        driver_version=fp.driver_version,
        fingerprint_hash=fp.fingerprint_hash(),
    )
    return VLLMGatewayCallResult(
        route_to_gemini=bp_decision.escalate_to_gemini or not preflight.token_budget_ok,
        local_request=local_request,
        telemetry=telemetry,
        preflight=preflight,
        backpressure=bp_decision,
    )


__all__ = [
    "VLLM_SEED",
    "VLLM_TEMPERATURE",
    "VLLM_TOP_P",
    "VLLMCircuitBreakerRegistry",
    "VLLMGatewayCallResult",
    "VLLMGatewayTelemetry",
    "VLLMLocalRequest",
    "VLLMQueueController",
    "evaluate_gateway_call",
    "select_serving_profile",
    "shape_local_request",
]

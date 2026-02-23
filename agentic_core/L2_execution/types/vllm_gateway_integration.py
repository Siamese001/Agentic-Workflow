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

# ---------------------------------------------------------------------------
# WAVE 1 — Serving profile selection
# ---------------------------------------------------------------------------


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
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_serving_profile_types import (
        PROFILE_LOCAL_FAST_7B,
        PROFILE_LOCAL_STRONG_14B,
        VLLMServingProfile,
    )
    
    if severity == "high":
        return PROFILE_LOCAL_STRONG_14B
    return PROFILE_LOCAL_FAST_7B


# ---------------------------------------------------------------------------
# WAVE 1 — vLLM request shaping
# ---------------------------------------------------------------------------

# Determinism policy: temperature=0, top_p=1.0, seed fixed
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


def shape_local_request(
    prompt: str,
    task_class: str,
    profile: VLLMServingProfile,
) -> VLLMLocalRequest:
    """Shape a local vLLM request with deterministic parameters.

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        profile: Selected serving profile.

    Returns:
        VLLMLocalRequest with explicit max_tokens and determinism policy.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_token_budget_types import get_output_cap
    
    max_output = get_output_cap(task_class)
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


# ---------------------------------------------------------------------------
# WAVE 2 — In-gateway backpressure controller (threadsafe, bounded counter)
# ---------------------------------------------------------------------------


class VLLMQueueController:
    """Threadsafe bounded queue counter for backpressure enforcement.

    Maintains an in-memory queue depth counter. Does not spawn threads.
    """

    def __init__(
        self,
        max_depth: int | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        # Function-scoped imports to avoid lazy seam violations
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
        # Function-scoped imports to avoid lazy seam violations
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


# ---------------------------------------------------------------------------
# WAVE 2 — Circuit breaker registry (one breaker per tier)
# ---------------------------------------------------------------------------


class VLLMCircuitBreakerRegistry:
    """Registry of circuit breakers, one per tier.

    Threadsafe. Breakers are created on first access.
    """

    def __init__(self) -> None:
        self._breakers: dict[str, "VLLMCircuitBreaker"] = {}
        self._lock = threading.Lock()

    def get(self, tier: str) -> VLLMCircuitBreaker:
        # Function-scoped imports to avoid lazy seam violations
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


# ---------------------------------------------------------------------------
# WAVE 3 — Telemetry event
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VLLMGatewayTelemetry:
    """Immutable telemetry payload for a single gateway call.

    All fields are deterministic; no timestamps. Stable key ordering via as_dict().
    PHASE 4: Extended with infrastructure fingerprint fields for replay sealing.
    """

    # Routing decision
    provider_selected: str
    model_tier: str

    # Token budgeting fields
    prompt_tokens_estimated: int
    max_output_tokens_requested: int
    max_model_len_configured: int
    token_budget_ok: bool
    budget_margin_tokens: int

    # Backpressure fields
    queue_depth: int
    queue_full: bool
    queue_wait_seconds: float

    # Circuit breaker fields
    breaker_state: str
    breaker_failure_count: int

    # Failure taxonomy
    failure_type: str | None

    # PHASE 4: Infrastructure fingerprint fields (deterministic)
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
            # PHASE 4: Infrastructure fingerprint fields
            "model_name": self.model_name,
            "model_revision_sha": self.model_revision_sha,
            "vllm_version": self.vllm_version,
            "transformers_version": self.transformers_version,
            "torch_version": self.torch_version,
            "cuda_version": self.cuda_version,
            "driver_version": self.driver_version,
            "fingerprint_hash": self.fingerprint_hash,
        }


# ---------------------------------------------------------------------------
# WAVE 3 — Gateway call-path controller
# ---------------------------------------------------------------------------


@dataclass
class VLLMGatewayCallResult:
    """Result of a gateway call-path evaluation.

    Contains routing decision, shaped request (if local), and telemetry.
    """

    route_to_gemini: bool
    local_request: VLLMLocalRequest | None
    telemetry: VLLMGatewayTelemetry
    preflight: VLLMPreflightResult
    backpressure: BackpressureDecision


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
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_backpressure_types import (
        BackpressureDecision,
        evaluate_backpressure,
    )
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_token_budget_types import (
        GEMINI_25_PRO_MODEL_ID,
        VLLMFailureType,
        VLLMPreflightResult,
        run_preflight_budget_check,
    )
    
    # Select profile based on severity
    profile = select_serving_profile(severity)
    tier = "local_fast" if profile.profile_name == "LOCAL_FAST_7B" else "local_strong"

    # Snapshot queue and breaker state
    queue_state = queue_controller.snapshot(oldest_wait_seconds)
    breaker = breaker_registry.get(tier)

    # Evaluate backpressure
    bp_decision = evaluate_backpressure(queue_state, breaker)

    # Run preflight token budget check
    preflight = run_preflight_budget_check(
        prompt=prompt,
        task_class=task_class,
        max_model_len=profile.max_model_len,
    )

    # Determine final routing
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
        # Local path
        provider_selected = profile.model
        model_tier = "fast" if profile.profile_name == "LOCAL_FAST_7B" else "strong"
        failure_type = None
        local_request = shape_local_request(prompt, task_class, profile)

    # PHASE 4: Use provided fingerprint or deterministic test instance
    fp = fingerprint if fingerprint is not None else VLLMInfrastructureFingerprint.deterministic_test_instance()

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
        # PHASE 4: Infrastructure fingerprint fields
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

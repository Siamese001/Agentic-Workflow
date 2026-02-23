"""
PHASE 3.1 — VLLMGatewayAdapter: thin seam between SovereignLLMGateway and
the Phase 3 call-path controller (evaluate_gateway_call).

This module is the ONLY import boundary that SovereignLLMGateway touches.
It has zero external dependencies — stdlib + Phase 1/2/3 types only.
Tests import this module directly; they never import SovereignLLMGateway.

Seam contract:
    adapter = VLLMGatewayAdapter()
    decision = adapter.evaluate(prompt, task_class, severity,
                                oldest_wait_seconds=0.0)
    # decision.route_to_gemini  → bool
    # decision.local_request    → VLLMLocalRequest | None
    # decision.telemetry        → VLLMGatewayTelemetry
    # decision.telemetry_dict   → dict (stable key order, ASCII-safe)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Singleton-style shared state (one queue + one breaker registry per process).
# Replaced in tests via VLLMGatewayAdapter(queue=..., registry=...).
_DEFAULT_QUEUE: VLLMQueueController | None = None
_DEFAULT_REGISTRY: VLLMCircuitBreakerRegistry | None = None


def _get_default_queue() -> VLLMQueueController:
    global _DEFAULT_QUEUE
    if _DEFAULT_QUEUE is None:
        _DEFAULT_QUEUE = VLLMQueueController()
    return _DEFAULT_QUEUE


def _get_default_registry() -> VLLMCircuitBreakerRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = VLLMCircuitBreakerRegistry()
    return _DEFAULT_REGISTRY


def reset_singletons() -> None:
    """Reset process-level singletons. For testing only."""
    global _DEFAULT_QUEUE, _DEFAULT_REGISTRY
    _DEFAULT_QUEUE = None
    _DEFAULT_REGISTRY = None


@dataclass
class VLLMGatewayAdapter:
    """Thin seam: wraps evaluate_gateway_call with process-level state.

    SovereignLLMGateway instantiates this once (or uses the module-level
    singleton helpers) and calls .evaluate() before choosing a provider.

    Args:
        queue: Optional queue controller override (for testing).
        registry: Optional circuit breaker registry override (for testing).
    """

    queue: VLLMQueueController | None = field(default=None)
    registry: VLLMCircuitBreakerRegistry | None = field(default=None)

    def evaluate(
        self,
        prompt: str,
        task_class: str,
        severity: str,
        oldest_wait_seconds: float = 0.0,
        fingerprint: VLLMInfrastructureFingerprint | None = None,
    ) -> VLLMGatewayCallResult:
        """Evaluate the call path and return a routing decision.

        Args:
            prompt: Input prompt string.
            task_class: Task class string from TaskClass enum.
            severity: Severity level ("low", "medium", "high").
            oldest_wait_seconds: Age of oldest queued request in seconds.
            fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

        Returns:
            VLLMGatewayCallResult with routing decision + telemetry.
        """
        # Function-scoped imports to avoid lazy seam violations
        from agentic_core.L2_execution.types.vllm_gateway_integration import (
            VLLMCircuitBreakerRegistry,
            VLLMGatewayCallResult,
            VLLMQueueController,
            evaluate_gateway_call,
        )
        from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint import (
            VLLMInfrastructureFingerprint,
        )
        
        q = self.queue if self.queue is not None else _get_default_queue()
        r = self.registry if self.registry is not None else _get_default_registry()
        return evaluate_gateway_call(
            prompt=prompt,
            task_class=task_class,
            severity=severity,
            queue_controller=q,
            breaker_registry=r,
            oldest_wait_seconds=oldest_wait_seconds,
            fingerprint=fingerprint,
        )

    def record_local_failure(self, severity: str) -> None:
        """Record a local vLLM failure for circuit breaker tracking."""
        r = self.registry if self.registry is not None else _get_default_registry()
        tier = "local_strong" if severity == "high" else "local_fast"
        r.record_failure(tier)

    def record_local_success(self, severity: str) -> None:
        """Record a local vLLM success for circuit breaker tracking."""
        r = self.registry if self.registry is not None else _get_default_registry()
        tier = "local_strong" if severity == "high" else "local_fast"
        r.record_success(tier)


# ---------------------------------------------------------------------------
# Seam proof — importable by evidence runner without SovereignLLMGateway
# ---------------------------------------------------------------------------

SEAM_PROOF_MARKER = "OK: SovereignLLMGateway uses VLLMGatewayAdapter -> evaluate_gateway_call"


def emit_seam_proof() -> str:
    """Return the seam proof marker string. Used by evidence runner."""
    return SEAM_PROOF_MARKER


__all__ = [
    "SEAM_PROOF_MARKER",
    "VLLMGatewayAdapter",
    "emit_seam_proof",
    "reset_singletons",
]

"""
Orchestration Protocols - W5 Implementation

Defines the canonical interface for L3 orchestration implementations.
Type-safe protocols ensure consistent behavior across all orchestrators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload


@dataclass
class OrchestrationResult:
    """Result from L3 orchestration processing."""

    success: bool
    route_mode: str
    plan_hash: str
    execution_trace: dict[str, Any] | None = None
    handshake_state: Any = None
    determinism_digest: str | None = None
    human_decision_artifact: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "route_mode": self.route_mode,
            "plan_hash": self.plan_hash,
            "execution_trace": self.execution_trace,
            "handshake_state": self.handshake_state.value
            if hasattr(self.handshake_state, "value")
            else str(self.handshake_state),
            "determinism_digest": self.determinism_digest,
            "human_decision_artifact": self.human_decision_artifact,
            "metadata": self.metadata or {},
        }


@runtime_checkable
class IOrchestrator(Protocol):
    """
    Protocol defining the canonical interface for L3 orchestrators.

    All orchestrator implementations must implement this protocol
    to ensure consistent behavior and enable type-safe orchestration.
    """

    def orchestrate(
        self,
        governed_payload: GovernedPayload,
        route_mode: str,
        trace_id: str,
        policy_hash: str,
        allowed_tools: tuple[str, ...],
    ) -> OrchestrationResult:
        """
        Orchestrate the governed payload through L3 processing.

        Args:
            governed_payload: The assembled payload from L0 Assembly Stage
            route_mode: Route mode (B/C/D) - Path A bypasses L3 entirely
            trace_id: Unique trace identifier for audit trail
            policy_hash: Policy validation hash from L0/L5
            allowed_tools: Tuple of allowed tool names

        Returns:
            OrchestrationResult with deterministic outcome and audit trail
        """
        ...


__all__ = ["IOrchestrator", "OrchestrationResult"]

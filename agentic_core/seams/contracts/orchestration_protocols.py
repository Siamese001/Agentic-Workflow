"""
Orchestration Protocols - W5 Implementation

Defines the canonical interface for L3 orchestration implementations.
Type-safe protocols ensure consistent behavior across all orchestrators.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, Protocol, runtime_checkable

if TYPE_CHECKING:
    from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload
else:
    GovernedPayload = Any


def _serialize_handshake_state(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _serialize_handshake_state(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_handshake_state(v) for v in value]
    return repr(value)


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """Result from L3 orchestration processing."""

    success: bool
    route_mode: str
    plan_hash: str
    execution_trace: Mapping[str, Any] | None = None
    handshake_state: Any = None
    determinism_digest: str | None = None
    human_decision_artifact: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serialization-safe dictionary."""
        return {
            "success": self.success,
            "route_mode": self.route_mode,
            "plan_hash": self.plan_hash,
            "execution_trace": deepcopy(dict(self.execution_trace))
            if self.execution_trace is not None
            else None,
            "handshake_state": _serialize_handshake_state(self.handshake_state),
            "determinism_digest": self.determinism_digest,
            "human_decision_artifact": deepcopy(dict(self.human_decision_artifact))
            if self.human_decision_artifact is not None
            else None,
            "metadata": deepcopy(dict(self.metadata)) if self.metadata is not None else {},
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

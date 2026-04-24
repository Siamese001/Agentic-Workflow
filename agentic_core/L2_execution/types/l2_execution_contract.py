"""
L2 Execution Contract - Canonical execution taxonomy for L2 subphases.

Standardizes all L2 execution agents to follow the same phase contract:
INIT → EXECUTE → EVALUATE/HEAL → SYNTHESIZE

This module defines the canonical L2 execution phases and the contract interface
that all L2 execution-capable agents must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "L2ExecutionPhase",
    "L2PhaseResult",
    "L2ExecutionContext",
    "L2ExecutionContract",
    "L2ExecutionAgent",
    "CanonicalAgentRole",
    "FailureSignal",
    "HealingInput",
    "HealingDecision",
    "HealingTier",
]


@dataclass(frozen=True, slots=True)
class FailureSignal:
    """Signal representing a failure with retry context."""

    failure_type: str
    retry_count: int
    blast_radius_estimate: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_healing_input(self) -> "HealingInput":
        """Convert failure signal to healing input."""
        return HealingInput(
            failure_type=self.failure_type,
            blast_radius_estimate=self.blast_radius_estimate,
            metadata=self.metadata,
        )


@dataclass
class HealingInput:
    """Input for healing decision making."""

    failure_type: str
    blast_radius_estimate: float
    metadata: dict[str, Any] = field(default_factory=dict)


class HealingTier(Enum):
    """Healing tier classification."""

    LOCAL_AGENT = "local_agent"
    WORKFLOW = "workflow"
    ORCHESTRATION = "orchestration"
    MANUAL = "manual"


@dataclass
class HealingDecision:
    """Decision on how to handle healing."""

    tier: HealingTier
    reason_codes: list[str] = field(default_factory=list)


class L2ExecutionPhase(Enum):
    """
    Canonical L2 execution subphases aligned to process map.

    L2.1 INIT - Pre-commit setup, validation, context assembly
    L2.2 EXECUTE - Core business logic execution
    L2.3 EVALUATE_HEAL - Post-execution evaluation and healing
    L2.4 SYNTHESIZE - Result synthesis and handoff preparation
    """

    INIT = auto()
    EXECUTE = auto()
    EVALUATE_HEAL = auto()
    SYNTHESIZE = auto()


@dataclass(frozen=True, slots=True)
class L2PhaseResult:
    """Immutable result from an L2 execution phase."""

    phase: L2ExecutionPhase
    success: bool
    output: Any = None
    failure_signal: FailureSignal | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class L2ExecutionContext:
    """
    Shared context passed through all L2 execution phases.

    This context is mutated in-place through phase progression but
    has deterministic snapshots at phase boundaries for traceability.
    """

    agent_id: str
    trace_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    phase_results: dict[L2ExecutionPhase, L2PhaseResult] = field(default_factory=dict)
    heal_enabled: bool = False
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def record_phase_result(self, result: L2PhaseResult) -> None:
        """Record a phase result and update context state."""
        self.phase_results[result.phase] = result
        if result.failure_signal:
            self.retry_count = result.failure_signal.retry_count

    def should_attempt_heal(self) -> bool:
        """
        Determine if healing should be attempted based on context state.

        Healing is attempted when:
        - heal_enabled flag is True (from --heal or equivalent)
        - retry count is within budget
        - last phase had a recoverable failure
        """
        if not self.heal_enabled:
            return False
        if self.retry_count >= self.max_retries:
            return False

        # Check if last phase had a recoverable failure
        last_phase = max(
            (p for p in L2ExecutionPhase if p in self.phase_results),
            key=lambda p: list(L2ExecutionPhase).index(p),
            default=None,
        )
        if last_phase and last_phase in self.phase_results:
            result = self.phase_results[last_phase]
            if result.failure_signal:
                # Only heal if failure is classified as recoverable
                return result.failure_signal.failure_type not in (
                    "UNRECOVERABLE",
                    "ARCHITECTURE_VIOLATION",
                    "L5_HARD_DENY",
                )
        return False


@runtime_checkable
class L2ExecutionContract(Protocol):
    """
    Protocol defining the L2 execution contract.

    All L2 execution-capable agents must implement this interface.
    The contract ensures consistent phase execution across all agents.
    """

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """L2.1: Pre-commit initialization and validation."""
        ...

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """L2.2: Core execution logic."""
        ...

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        """L2.3: Post-execution evaluation and healing if needed."""
        ...

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        """L2.4: Result synthesis and handoff preparation."""
        ...

    def run_l2_phases(
        self,
        inputs: dict[str, Any],
        heal_enabled: bool = False,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run all L2 phases with automatic phase progression.

        This is the main entry point for L2 execution.
        """
        ...


class CanonicalAgentRole(Enum):
    """
    Canonical taxonomy roles for all agents in the system.

    Every agent must belong to exactly one of these roles.
    """

    PLANNER = "planner"  # L1: Planning and strategy
    ROUTER = "router"  # L0: Routing and dispatch
    EXECUTION = "execution"  # L2: Execution and healing
    HEAL = "heal"  # L2: Dedicated healing
    ORCHESTRATOR = "orchestrator"  # L3: Workflow orchestration
    SAFETY = "safety"  # L5: Policy/safety enforcement
    OBSERVER = "observer"  # L6: Observation and evaluation


import uuid


class L2ExecutionAgent(ABC):
    """
    Abstract base class for L2 execution agents.

    Implements the L2ExecutionContract with default behavior.
    Subclasses override specific phase methods while inheriting
    the canonical phase orchestration.
    """

    canonical_role: CanonicalAgentRole = CanonicalAgentRole.EXECUTION
    agent_layer: str = "L2"

    def __init__(self, agent_id: str | None = None):
        self.agent_id = agent_id or self.__class__.__name__

    def run_l2_phases(
        self,
        inputs: dict[str, Any],
        heal_enabled: bool = False,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute all L2 phases with automatic progression and healing.

        This is the canonical execution path that all L2 agents follow.
        """
        context = L2ExecutionContext(
            agent_id=self.agent_id,
            trace_id=trace_id or self._generate_trace_id(),
            inputs=inputs,
            heal_enabled=heal_enabled,
        )

        # L2.1: INIT
        init_result = self.l2_init(context)
        context.record_phase_result(init_result)
        if not init_result.success:
            return self._build_final_result(context, interrupted_at=L2ExecutionPhase.INIT)

        # E2: validate-before-execute short-circuit (W1-P1.3, gap plan b7c4e2 G8).
        # Opt-in: only engaged when ``inputs["tool_contract"]`` is a ToolContract.
        # Raises ConfirmBeforeExecute / E2RejectedBeforeExecute for high-consequence
        # or irreversible-non-read tools without an attached HITL approval ticket.
        e2_short_circuit = self._maybe_gate_e2(context)
        if e2_short_circuit is not None:
            context.record_phase_result(e2_short_circuit)
            return self._build_final_result(context, interrupted_at=L2ExecutionPhase.INIT)

        # L2.2: EXECUTE
        execute_result = self.l2_execute(context)
        context.record_phase_result(execute_result)

        # L2.3: EVALUATE/HEAL (if needed and enabled)
        if context.should_attempt_heal() and execute_result.failure_signal:
            heal_result = self.l2_evaluate_and_heal(context)
            context.record_phase_result(heal_result)
            if not heal_result.success:
                return self._build_final_result(context, interrupted_at=L2ExecutionPhase.EVALUATE_HEAL)
        elif not execute_result.success:
            # Failure but healing not enabled or not applicable
            return self._build_final_result(context, interrupted_at=L2ExecutionPhase.EXECUTE)

        # L2.4: SYNTHESIZE
        synthesize_result = self.l2_synthesize(context)
        context.record_phase_result(synthesize_result)

        return self._build_final_result(context)

    @abstractmethod
    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Override: Pre-commit initialization and validation."""
        raise NotImplementedError

    @abstractmethod
    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Override: Core execution logic."""
        raise NotImplementedError

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        Default healing implementation using simple retry logic.

        Subclasses can override for agent-specific healing logic,
        but must respect the heal_enabled flag and retry budget.
        """
        # Default implementation delegates to simple retry
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or not last_result.failure_signal:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                output=None,
                metadata={"heal_skipped": "no_failure_signal"},
            )

        # Simple local retry if within budget
        if context.retry_count < context.max_retries:
            return self._execute_local_heal(context)
        else:
            # Retry budget exhausted
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=False,
                failure_signal=last_result.failure_signal,
                metadata={"heal_skipped": "retry_budget_exhausted"},
            )

    def _execute_local_heal(
        self,
        context: L2ExecutionContext,
    ) -> L2PhaseResult:
        """Execute local agent healing - subclasses override for specific logic."""
        # Default: retry the execute phase once
        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            failure_signal=retry_result.failure_signal if not retry_result.success else None,
            metadata={
                "heal_attempted": True,
                "heal_tier": "LOCAL_AGENT",
                "retry_count": context.retry_count,
            },
        )

    @abstractmethod
    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Override: Result synthesis and handoff preparation."""
        raise NotImplementedError

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID for this execution."""
        return f"{self.agent_id}-{uuid.uuid4().hex[:8]}"

    def _maybe_gate_e2(
        self,
        context: "L2ExecutionContext",
    ) -> "L2PhaseResult | None":
        """W1-P1.3: run the E2 validate-before-execute gate if a ToolContract is
        attached to ``context.inputs["tool_contract"]``. Returns a non-None
        ``L2PhaseResult`` to short-circuit; returns None to continue to E3.

        The gate is entirely opt-in — the default L2 code path is unchanged
        when no ``tool_contract`` is attached. Imports are local to avoid
        creating a hot dependency on the W1 safety modules for agents that
        don't use the gate yet.
        """
        tool_contract = context.inputs.get("tool_contract")
        if tool_contract is None:
            return None

        # Local import: keeps the base class loadable even when the W1
        # safety modules are not present (e.g. legacy subset imports).
        try:
            from agentic_core.L2_execution.enforcement.e2_validate_before_execute import (  # noqa: PLC0415
                ConfirmBeforeExecute,
                E2RejectedBeforeExecute,
                evaluate_work_order,
            )
            from agentic_core.L2_execution.types.execution_tool_contract import (  # noqa: PLC0415
                ToolContract,
            )
        except ImportError:  # guardian: allow-return-none-swallow -- safety modules not importable; fail open to preserve legacy behavior, audited via absence of gate metadata on returned L2PhaseResult
            return None

        if not isinstance(tool_contract, ToolContract):
            return None

        try:
            verdict = evaluate_work_order(tool_contract)
        except ConfirmBeforeExecute as exc:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                output=None,
                metadata={
                    "e2_gate": "confirm_required",
                    "verdict": exc.verdict.to_dict(),
                    "needs_hitl_confirmation": True,
                },
            )
        except E2RejectedBeforeExecute as exc:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                output=None,
                metadata={
                    "e2_gate": "rejected",
                    "verdict": exc.verdict.to_dict(),
                    "needs_hitl_confirmation": False,
                },
            )

        # Approved — record in phase metadata so downstream observers see
        # the gate ran, then continue to E3.
        context.metadata.setdefault("e2_verdicts", []).append(verdict.to_dict())
        return None

    def _build_final_result(
        self,
        context: L2ExecutionContext,
        interrupted_at: L2ExecutionPhase | None = None,
    ) -> dict[str, Any]:
        """Build the final result dictionary from phase results."""
        result = {
            "agent_id": context.agent_id,
            "trace_id": context.trace_id,
            "success": interrupted_at is None,
            "phases_completed": [p.name for p in context.phase_results.keys()],
            "phase_results": {
                p.name: {
                    "success": r.success,
                    "output": r.output,
                    "failure_type": r.failure_signal.failure_type if r.failure_signal else None,
                }
                for p, r in context.phase_results.items()
            },
            "heal_enabled": context.heal_enabled,
            "retry_count": context.retry_count,
            "metadata": context.metadata,
        }

        if interrupted_at:
            result["interrupted_at"] = interrupted_at.name
            result["success"] = False

        return result

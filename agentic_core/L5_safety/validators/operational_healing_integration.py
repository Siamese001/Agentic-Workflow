"""
Operational Healing Integration Module - Final Orphan Agent Rewiring

Integrates remaining orphan agents into the healing infrastructure:
- HistorianAgent: Event logging strategy
- CostGovernorAgent: Budget tracking strategy
- DecompositionOrchestratorAgent: Task decomposition strategy

These agents have valuable functionality that should be preserved
through integration rather than deletion.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

Logger = logging.getLogger(__name__)


class HealingStrategyProtocol(Protocol):
    """Protocol for healing strategies."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


class HistorianLoggingStrategy:
    """
    Healing strategy that logs validation events using HistorianAgent.

    Wraps HistorianAgent to provide event logging as a healing strategy.
    """

    SUPPORTED_VIOLATIONS = frozenset(
        {
            "audit_required",
            "event_logging",
            "validation_record",
            "history_tracking",
        }
    )

    def __init__(self) -> None:
        """Initialize the historian logging strategy."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L2_execution.tool_registry.HistorianAgent import (
                HistorianAgent,
            )

            class MockContext:
                pass

            self._agent = HistorianAgent(ctx=MockContext())
            self._initialized = True
        except Exception as e:
            Logger.warning(f"[HistorianLoggingStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can handle the violation."""
        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """Log the violation event using HistorianAgent."""
        self._ensure_initialized()

        if self._agent is None:
            return {
                "success": True,
                "status": "agent_unavailable",
                "logged": False,
            }

        try:
            agent_name = violation.get("agent", "Unknown")
            status = violation.get("status", "recorded")
            details = violation.get("details", str(violation))

            self._agent.record_event(agent_name, status, details)

            return {
                "success": True,
                "logged": True,
                "agent": agent_name,
                "status": status,
            }

        except Exception as e:
            Logger.error(f"[HistorianLoggingStrategy] Logging failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "logged": False,
            }


class CostGovernorStrategy:
    """
    Healing strategy that tracks costs using CostGovernorAgent.

    Wraps CostGovernorAgent to provide budget tracking as a healing strategy.
    """

    SUPPORTED_VIOLATIONS = frozenset(
        {
            "cost_tracking",
            "budget_check",
            "spend_audit",
            "financial_validation",
        }
    )

    def __init__(self, budget_limit: float = 10.0) -> None:
        """Initialize the cost governor strategy."""
        self._agent = None
        self._initialized = False
        self._budget_limit = budget_limit

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L5_safety.guardrails.CostGovernorAgent import (
                CostGovernorAgent,
            )

            self._agent = CostGovernorAgent(config={"budget_limit": self._budget_limit})
            self._initialized = True
        except Exception as e:
            Logger.warning(f"[CostGovernorStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can handle the violation."""
        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """Track costs using CostGovernorAgent."""
        self._ensure_initialized()

        if self._agent is None:
            return {
                "success": True,
                "status": "agent_unavailable",
                "tracked": False,
            }

        try:
            model = violation.get("model", "unknown")
            input_tokens = violation.get("input_tokens", 0)
            output_tokens = violation.get("output_tokens", 0)

            cost = self._agent.track(model, input_tokens, output_tokens)

            return {
                "success": True,
                "tracked": True,
                "cost": cost,
                "total_spend": self._agent.spend,
                "budget_limit": self._agent.limit,
                "budget_remaining": self._agent.limit - self._agent.spend,
            }

        except Exception as e:
            error_msg = str(e)
            is_budget_exceeded = "BUDGET EXCEEDED" in error_msg

            return {
                "success": not is_budget_exceeded,
                "error": error_msg,
                "budget_exceeded": is_budget_exceeded,
                "tracked": True,
            }


class TaskDecompositionStrategy:
    """
    Healing strategy that decomposes tasks using DecompositionOrchestratorAgent.

    Wraps DecompositionOrchestratorAgent to provide task decomposition
    as a healing strategy for complex violations.
    """

    SUPPORTED_VIOLATIONS = frozenset(
        {
            "task_decomposition",
            "complex_healing",
            "multi_step_fix",
            "orchestrated_repair",
        }
    )

    def __init__(self) -> None:
        """Initialize the task decomposition strategy."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L3_orchestration.workflow_engines.DecompositionOrchestratorAgent import (  # noqa: E501
                DecompositionOrchestratorAgent,
            )

            self._agent = DecompositionOrchestratorAgent()
            self._initialized = True
        except Exception as e:
            Logger.warning(f"[TaskDecompositionStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can handle the violation."""
        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """Decompose the healing task using DecompositionOrchestratorAgent."""
        self._ensure_initialized()

        if self._agent is None:
            return {
                "success": True,
                "status": "agent_unavailable",
                "decomposed": False,
            }

        try:
            prompt = violation.get("prompt", violation.get("description", ""))
            if not prompt:
                prompt = f"Heal violation: {violation.get('type', 'unknown')}"

            max_tasks = context.get("max_tasks", 5)
            dry_run = context.get("dry_run", True)

            # Decompose the task
            plan = self._agent.decompose(prompt, max_tasks=max_tasks)

            # Execute if not dry run
            if not dry_run:
                result = self._agent.execute(plan, dry_run=False)
            else:
                result = self._agent.execute(plan, dry_run=True)

            return {
                "success": True,
                "decomposed": True,
                "mission_id": plan.mission_id,
                "tasks_count": len(plan.tasks),
                "execution_result": result,
                "dry_run": dry_run,
            }

        except Exception as e:
            Logger.error(f"[TaskDecompositionStrategy] Decomposition failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "decomposed": False,
            }


# Global strategy instances (lazy-initialized)
_historian_strategy: HistorianLoggingStrategy | None = None
_cost_governor_strategy: CostGovernorStrategy | None = None
_decomposition_strategy: TaskDecompositionStrategy | None = None


def get_historian_strategy() -> HistorianLoggingStrategy:
    """Get or create the historian logging strategy instance."""
    global _historian_strategy
    if _historian_strategy is None:
        _historian_strategy = HistorianLoggingStrategy()
    return _historian_strategy


def get_cost_governor_strategy(budget_limit: float = 10.0) -> CostGovernorStrategy:
    """Get or create the cost governor strategy instance."""
    global _cost_governor_strategy
    if _cost_governor_strategy is None:
        _cost_governor_strategy = CostGovernorStrategy(budget_limit)
    return _cost_governor_strategy


def get_decomposition_strategy() -> TaskDecompositionStrategy:
    """Get or create the task decomposition strategy instance."""
    global _decomposition_strategy
    if _decomposition_strategy is None:
        _decomposition_strategy = TaskDecompositionStrategy()
    return _decomposition_strategy


def register_operational_healing() -> dict[str, Any]:
    """
    Register all operational healing strategies with the orchestrator.

    Returns:
        dict with registration status
    """
    registered = []
    errors = []

    try:
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()

        # Register historian strategy
        try:
            orchestrator.register_strategy("historian_logging", get_historian_strategy())
            registered.append("historian_logging")
        except Exception as e:
            errors.append(f"historian_logging: {e}")

        # Register cost governor strategy
        try:
            orchestrator.register_strategy("cost_governor", get_cost_governor_strategy())
            registered.append("cost_governor")
        except Exception as e:
            errors.append(f"cost_governor: {e}")

        # Register decomposition strategy
        try:
            orchestrator.register_strategy("task_decomposition", get_decomposition_strategy())
            registered.append("task_decomposition")
        except Exception as e:
            errors.append(f"task_decomposition: {e}")

        Logger.info(f"[Operational Integration] Registered {len(registered)} strategies")

    except ImportError as e:
        errors.append(f"HealingSovereignOrchestrator import failed: {e}")
        Logger.warning(f"[Operational Integration] Could not import orchestrator: {e}")

    return {
        "registered": registered,
        "errors": errors,
        "success": len(errors) == 0,
    }


def get_integration_status() -> dict[str, Any]:
    """Get the current status of operational healing integration."""
    return {
        "historian_strategy_initialized": _historian_strategy is not None,
        "cost_governor_strategy_initialized": _cost_governor_strategy is not None,
        "decomposition_strategy_initialized": _decomposition_strategy is not None,
        "strategies_available": [
            "historian_logging",
            "cost_governor",
            "task_decomposition",
        ],
    }

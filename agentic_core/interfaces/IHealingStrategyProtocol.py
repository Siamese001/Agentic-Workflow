"""
Chaos Healing Integration Module - Phase 1 Foundation

Registers ChaosEngineeringAgent as a healing strategy in the
HealingSovereignOrchestrator.

This module adapts the ChaosEngineeringAgent to the HealingStrategy
protocol, enabling resilience testing after healing operations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


def _run_agent(agent) -> dict:
    """Run an async agent's act() method in a dedicated event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(agent.act())
    finally:
        loop.close()


class IHealingStrategyProtocol(Protocol):
    """Protocol for healing strategies - matches HealingSovereignOrchestrator interface."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


class ChaosResilienceStrategy:
    """
    Healing strategy that validates system resilience after healing.

    Use case: After a healing operation completes, run chaos tests
    to verify the system can handle failures gracefully.
    """

    SUPPORTED_VIOLATIONS = frozenset(
        {"resilience_check", "post_healing_validation", "chaos_test_required", "system_stability_check"},
    )

    def __init__(self) -> None:
        """Initialize the chaos resilience strategy."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return
        try:
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.ChaosEngineeringAgent_validator import ChaosEngineeringAgent

            ctx = ValidationContext()
            self._agent = ChaosEngineeringAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[ChaosResilienceStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """
        Check if this strategy can handle the violation.

        Args:
            violation: Violation details with 'type' key

        Returns:
            True if this strategy can handle the violation type
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ChaosResilienceStrategy.can_heal"
        )

        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """
        Run chaos tests and report resilience status.

        Args:
            violation: Violation details
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        """
        self._ensure_initialized()
        if self._agent is None:
            return {
                "success": True,
                "resilience_score": 1.0,
                "status": "agent_unavailable",
                "scenarios_tested": 0,
            }
        try:
            result = _run_agent(self._agent)
            failures = result.get("failures_detected", 0)
            tests_executed = max(1, result.get("tests_executed", 1))
            recovery_metrics = result.get("recovery_metrics", {})
            return {
                "success": failures == 0,
                "resilience_score": 1.0 - failures / tests_executed,
                "recovery_metrics": recovery_metrics,
                "scenarios_tested": len(result.get("scenarios_tested", [])),
                "failures_detected": failures,
            }
        except (ValueError, TypeError, RuntimeError) as e:
            Logger.error(f"[ChaosResilienceStrategy] Healing failed: {e}")
            return {"success": False, "resilience_score": 0.0, "error": str(e), "scenarios_tested": 0}


_chaos_strategy: ChaosResilienceStrategy | None = None


def get_chaos_strategy() -> ChaosResilienceStrategy:
    """Get or create the chaos resilience strategy instance."""
    global _chaos_strategy
    if _chaos_strategy is None:
        _chaos_strategy = ChaosResilienceStrategy()
    return _chaos_strategy


def register_chaos_healing() -> dict[str, Any]:
    """
    Register chaos engineering as a healing strategy.

    Returns:
        dict with registration status
    """
    registered: list[str] = []
    errors: list[str] = []

    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import get_healing_orchestrator
    except ImportError as exc:
        errors.append(f"HealingSovereignOrchestrator import failed: {exc}")
        Logger.warning("[Chaos Integration] Could not import orchestrator: %s", exc)
        return {"registered": registered, "errors": errors, "success": False}

    orchestrator = get_healing_orchestrator()

    try:
        orchestrator.register_strategy("chaos_resilience", get_chaos_strategy())
        registered.append("chaos_resilience")
    except (ValueError, TypeError, RuntimeError) as exc:
        errors.append(f"chaos_resilience: {exc}")

    Logger.info("[Chaos Integration] Registered %s strategies", len(registered))
    return {"registered": registered, "errors": errors, "success": not errors}


def get_integration_status() -> dict[str, Any]:
    """Get the current status of chaos healing integration."""
    return {
        "chaos_strategy_initialized": _chaos_strategy is not None,
        "strategies_available": ["chaos_resilience"],
        "supported_violations": list(ChaosResilienceStrategy.SUPPORTED_VIOLATIONS),
    }

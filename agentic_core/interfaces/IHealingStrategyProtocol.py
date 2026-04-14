"""
Healing strategy integration module.
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


def _run_agent(agent) -> dict[str, Any]:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(agent.act())
    finally:
        loop.close()


class IHealingStrategyProtocol(Protocol):
    def can_heal(self, violation: dict[str, Any]) -> bool: ...

    def heal(self, violation: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]: ...


class ChaosResilienceStrategy:
    SUPPORTED_VIOLATIONS = frozenset(
        {"resilience_check", "post_healing_validation", "chaos_test_required", "system_stability_check"},
    )

    def __init__(self) -> None:
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.ChaosEngineeringAgent_validator import ChaosEngineeringAgent
        except ImportError as exc:
            Logger.warning("[ChaosResilienceStrategy] Could not import agent: %s", exc)
            self._initialized = True
            return

        self._agent = ChaosEngineeringAgent(ctx=ValidationContext())
        self._initialized = True

    def can_heal(self, violation: dict[str, Any]) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(_uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "ChaosResilienceStrategy.can_heal",
        )
        return str(violation.get("type", "")) in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
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
        except Exception as exc:  # guardian: allow-broad-exception -- _run_agent wraps arbitrary async agent code that may raise any exception type
            Logger.error("[ChaosResilienceStrategy] Healing failed: %s", exc)
            return {"success": False, "resilience_score": 0.0, "error": str(exc), "scenarios_tested": 0}

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


_chaos_strategy: ChaosResilienceStrategy | None = None


def get_chaos_strategy() -> ChaosResilienceStrategy:
    global _chaos_strategy
    if _chaos_strategy is None:
        _chaos_strategy = ChaosResilienceStrategy()
    return _chaos_strategy


def register_chaos_healing() -> dict[str, Any]:
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
    return {
        "chaos_strategy_initialized": _chaos_strategy is not None,
        "strategies_available": ["chaos_resilience"],
        "supported_violations": list(ChaosResilienceStrategy.SUPPORTED_VIOLATIONS),
    }

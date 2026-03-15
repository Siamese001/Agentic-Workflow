"""
Healing Orchestration Suite - Phase 3 Resilience Integration

Provides a unified interface for running all healing strategies:
- Chaos resilience testing
- Dependency pruning
- Post-healing validation

This module creates a HealingOrchestrationSuite that coordinates
healing operations across multiple strategies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "healing_orchestration_types", "p0_governance")
_emit_snapshots_state("p0", "healing_orchestration_types", "state_snapshot")

Logger = logging.getLogger(__name__)


@dataclass
class HealingResult:
    """Result from a single healing operation."""

    strategy_name: str
    success: bool
    violations_found: int = 0
    violations_fixed: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class HealingSuiteResult:
    """Aggregated result from running the full healing suite."""

    overall_success: bool
    strategies_run: int
    strategies_succeeded: int
    strategies_failed: int
    total_violations_found: int
    total_violations_fixed: int
    results: list[HealingResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: float = 0.0


class HealingOrchestrationSuite:
    """
    Orchestrates healing operations across multiple strategies.

    Usage:
        suite = HealingOrchestrationSuite()
        result = suite.run_all(
            violation={"type": "resilience_check"},
            context={"dry_run": True}
        )
        if result.overall_success:
            print(f"Healed {result.total_violations_fixed} violations")
    """

    def __init__(self) -> None:
        """Initialize the healing orchestration suite."""
        self._strategies: dict[str, Any] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of healing strategies."""
        if self._initialized:
            return
        try:
            from agentic_core.L5_safety.validators.chaos_healing_integration_types import get_chaos_strategy

            self._strategies["chaos_resilience"] = get_chaos_strategy()
        except ImportError as e:
            Logger.warning(f"[HealingSuite] Could not import chaos strategy: {e}")
        try:
            from agentic_core.L5_safety.validators.dependency_healing_integration_types import (
                get_dependency_strategy,
            )

            self._strategies["dependency_pruning"] = get_dependency_strategy()
        except ImportError as e:
            Logger.warning(f"[HealingSuite] Could not import dependency strategy: {e}")
        self._initialized = True
        Logger.info(f"[HealingSuite] Initialized with {len(self._strategies)} strategies")

    def run_strategy(self, strategy_name: str, violation: dict, context: dict | None = None) -> HealingResult:
        """
        Run a specific healing strategy.

        Args:
            strategy_name: Name of the strategy to run
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingResult with healing details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HealingOrchestrationSuite.run_strategy"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HealingOrchestrationSuite.run_strategy".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._ensure_initialized()
        context = context or {}
        if strategy_name not in self._strategies:
            return HealingResult(
                strategy_name=strategy_name, success=False, errors=[f"Strategy '{strategy_name}' not found"]
            )
        strategy = self._strategies[strategy_name]
        if hasattr(strategy, "can_heal") and (not strategy.can_heal(violation)):
            return HealingResult(
                strategy_name=strategy_name,
                success=True,
                errors=[],
                metadata={"skipped": True, "reason": "violation_type_not_supported"},
            )
        try:
            result = strategy.heal(violation, context)
            return HealingResult(
                strategy_name=strategy_name,
                success=result.get("success", False),
                violations_found=result.get("violations_found", 1),
                violations_fixed=result.get("violations_fixed", 0) if result.get("success") else 0,
                errors=result.get("errors", []),
                metadata={
                    k: v
                    for k, v in result.items()
                    if k not in ("success", "violations_found", "violations_fixed", "errors")
                },
            )
        except Exception as e:
            Logger.error(f"[HealingSuite] Strategy {strategy_name} failed: {e}")
            return HealingResult(
                strategy_name=strategy_name, success=False, errors=[f"Strategy error: {str(e)}"]
            )

    def run_all(self, violation: dict, context: dict | None = None) -> HealingSuiteResult:
        """
        Run all applicable healing strategies for a violation.

        Args:
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingSuiteResult with aggregated results
        """
        import time

        self._ensure_initialized()
        context = context or {}
        start_time = time.time()
        results: list[HealingResult] = []
        for strategy_name in self._strategies:
            result = self.run_strategy(strategy_name, violation, context)
            results.append(result)
        execution_time = (time.time() - start_time) * 1000
        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded
        total_found = sum(r.violations_found for r in results)
        total_fixed = sum(r.violations_fixed for r in results)
        return HealingSuiteResult(
            overall_success=failed == 0,
            strategies_run=len(results),
            strategies_succeeded=succeeded,
            strategies_failed=failed,
            total_violations_found=total_found,
            total_violations_fixed=total_fixed,
            results=results,
            execution_time_ms=execution_time,
        )

    def run_resilience_check(self, context: dict | None = None) -> HealingResult:
        """
        Run chaos resilience check specifically.

        Args:
            context: Optional healing context

        Returns:
            HealingResult from chaos resilience strategy
        """
        return self.run_strategy("chaos_resilience", violation={"type": "resilience_check"}, context=context)

    def run_dependency_cleanup(self, dry_run: bool = True, context: dict | None = None) -> HealingResult:
        """
        Run dependency pruning specifically.

        Args:
            dry_run: If True, only report what would be done
            context: Optional additional context

        Returns:
            HealingResult from dependency pruning strategy
        """
        ctx = context or {}
        ctx["dry_run"] = dry_run
        return self.run_strategy("dependency_pruning", violation={"type": "unused_dependency"}, context=ctx)

    def get_available_strategies(self) -> list[str]:
        """Get list of available strategy names."""
        self._ensure_initialized()
        return list(self._strategies.keys())

    def get_status(self) -> dict[str, Any]:
        """Get current status of the healing suite."""
        self._ensure_initialized()
        return {
            "initialized": self._initialized,
            "strategies_available": list(self._strategies.keys()),
            "strategy_count": len(self._strategies),
        }


_healing_suite: HealingOrchestrationSuite | None = None


def get_healing_suite() -> HealingOrchestrationSuite:
    """Get or create the global healing orchestration suite."""
    global _healing_suite
    if _healing_suite is None:
        _healing_suite = HealingOrchestrationSuite()
    return _healing_suite


def run_healing_operation(violation: dict, context: dict | None = None) -> HealingSuiteResult:
    """
    Convenience function to run healing for a violation.

    Args:
        violation: Violation details to heal
        context: Optional healing context

    Returns:
        HealingSuiteResult with all healing results
    """
    suite = get_healing_suite()
    return suite.run_all(violation, context)

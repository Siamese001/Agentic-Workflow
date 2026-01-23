"""
HealingSovereignOrchestrator - Unified Healing Gateway

[PHASE 5 MIGRATION] Consolidates all healing operations:
- Strategy registration and dispatch
- Healing transaction management
- Metrics collection
- Audit logging with memory protection
- Recursion guardrails
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
import time
import logging

from agentic_core.config.SovereignConfigManager import get_sovereign_config

Logger = logging.getLogger(__name__)


class HealingStrategy(Protocol):
    """Protocol for healing strategies."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


@dataclass
class HealingSovereignOrchestrator:
    """
    Unified Healing Orchestrator - Single point of truth for all healing operations.

    [PHASE 5 MIGRATION] Absorbed from:
    - healing_strategies.py (9 strategies)
    - healing_healing_engine.py
    """

    _instance: HealingSovereignOrchestrator | None = None

    # [PHASE 6] Configuration now managed by SovereignConfigManager

    # State
    _strategies: dict[str, HealingStrategy] = field(default_factory=dict)

    operation_stats: dict[str, Any] = field(
        default_factory=lambda: {
            "total_heals": 0,
            "successful_heals": 0,
            "failed_heals": 0,
            "by_strategy": {},
        }
    )

    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset singleton state."""
        cls._instance = None

    @property
    def config(self):
        """[PHASE 6] Access centralized config."""
        return get_sovereign_config()

    def register_strategy(self, name: str, strategy: HealingStrategy) -> None:
        """Register a healing strategy."""
        self._strategies[name] = strategy
        if name not in self.operation_stats["by_strategy"]:
            self.operation_stats["by_strategy"][name] = {"attempts": 0, "successes": 0}
        Logger.info(f"[Healing Orchestrator] Registered strategy: {name}")

    def _audit(
        self, strategy_name: str, violation_type: str, success: bool, latency_ms: float
    ) -> None:
        """
        [PHASE 5] Record healing operation with FIFO memory protection.
        """
        # [PHASE 6] Dynamic limit from config
        limit = self.config.max_audit_log_size

        if len(self.audit_log) >= limit:
            # Prune 10%
            prune_count = max(1, int(limit * 0.1))
            self.audit_log = self.audit_log[prune_count:]

        self.audit_log.append(
            {
                "strategy": strategy_name,
                "violation_type": violation_type,
                "success": success,
                "latency_ms": latency_ms,
                "ts": time.time(),
            }
        )

        self.operation_stats["total_heals"] += 1
        if success:
            self.operation_stats["successful_heals"] += 1
        else:
            self.operation_stats["failed_heals"] += 1

        if strategy_name in self.operation_stats["by_strategy"]:
            stats = self.operation_stats["by_strategy"][strategy_name]
            stats["attempts"] += 1
            if success:
                stats["successes"] += 1

    async def heal(self, violation: dict, context: dict = None) -> dict:
        """
        Execute healing for a violation.

        [PHASE 5] Unified healing interface.
        """
        context = context or {}
        start = time.time()

        # [PHASE 6] Check recursion depth using config
        limit = self.config.max_healing_attempts
        depth = context.get("_healing_depth", 0)
        if depth >= limit:
            Logger.error(f"[Healing] Max depth {limit} reached. Aborting.")
            return {"status": "failed", "reason": "max_depth_exceeded"}

        # Increment depth for strategies that might call heal recursively
        context["_healing_depth"] = depth + 1

        # Find applicable strategy
        # Note: Iteration order depends on insertion order (Python 3.7+)
        # Future improvement: Add priority weights
        for name, strategy in self._strategies.items():
            try:
                if strategy.can_heal(violation):
                    result = strategy.heal(violation, context)

                    latency = (time.time() - start) * 1000
                    # Assuming result implies success if no exception,
                    # but strategies should return status.
                    # We treat dict return as success for basic protocol.
                    success = result.get("success", True)

                    self._audit(name, violation.get("type", "unknown"), success, latency)
                    return {"status": "healed", "strategy": name, "result": result}
            except Exception as e:
                latency = (time.time() - start) * 1000
                self._audit(name, violation.get("type", "unknown"), False, latency)
                Logger.error(f"[Healing] Strategy {name} failed: {e}")
                continue

        latency = (time.time() - start) * 1000
        self._audit("none", violation.get("type", "unknown"), False, latency)
        return {"status": "no_strategy", "violation": violation}


# Singleton accessor
def get_healing_orchestrator() -> HealingSovereignOrchestrator:
    """Get or create the global healing orchestrator."""
    return HealingSovereignOrchestrator()

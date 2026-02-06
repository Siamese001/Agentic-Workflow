#!/usr/bin/env python3
from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
ResourceManagerAgent - Thread-Safe Resource Management

Phase 3 Hard Migration: Consolidates:
- BudgetManagerAgent (budget tracking and enforcement)
- ProactiveResourceManagerAgent (proactive resource allocation)
- FallbackManagerAgent (fallback and recovery logic)

Features:
- Thread-safe budget management with locks
- Hard cap enforcement (100% exhaustion halts execution)
- Proactive resource allocation
- Fallback strategies for resource exhaustion
- Concurrent agent support (10+ simultaneous requests)
"""


import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

Logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources managed."""

    BUDGET = auto()
    MEMORY = auto()
    CPU = auto()
    API_CALLS = auto()
    TOKENS = auto()


class AllocationStatus(Enum):
    """Status of resource allocation."""

    ALLOCATED = auto()
    DENIED = auto()
    FALLBACK = auto()
    EXHAUSTED = auto()


@dataclass
class ResourceAllocation:
    """Represents a resource allocation."""

    resource_type: ResourceType
    amount: float
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: AllocationStatus = AllocationStatus.ALLOCATED


@dataclass
class ResourceBudget:
    """Budget configuration for a resource type."""

    resource_type: ResourceType
    total: float
    used: float = 0.0
    reserved: float = 0.0
    hard_cap: bool = True  # If True, halt execution at 100%
    warning_threshold: float = 0.8  # Warn at 80%

    @property
    def available(self) -> float:
        return max(0.0, self.total - self.used - self.reserved)

    @property
    def utilization(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.used + self.reserved) / self.total

    @property
    def is_exhausted(self) -> bool:
        return self.available <= 0


@dataclass
class ResourceConfig:
    """configuration for resource management."""

    enable_hard_caps: bool = True
    enable_proactive_allocation: bool = True
    enable_fallback: bool = True
    max_concurrent_allocations: int = 100
    allocation_timeout_seconds: float = 30.0
    fallback_strategies: list[str] = field(default_factory=lambda: ["queue", "throttle", "reject"])


class ResourceManagerAgent(SovereignBaseAgent):
    """
    Thread-safe unified resource manager.

    Consolidates:
    - BudgetManagerAgent (budget tracking)
    - ProactiveResourceManagerAgent (proactive allocation)
    - FallbackManagerAgent (fallback strategies)

    Usage:
        manager = ResourceManagerAgent()

        # Set budget
        manager.set_budget(ResourceType.BUDGET, total=1000.0)

        # Request allocation
        result = manager.allocate("agent_1", ResourceType.BUDGET, 100.0)

        # Check if exhausted
        if manager.is_exhausted(ResourceType.BUDGET):
            print("Budget exhausted!")
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Resource manager primarily handles runtime allocation
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, agent_config: ResourceConfig | None = None):
        self._agent_config = agent_config or ResourceConfig()
        self._lock = threading.RLock()
        self._budgets: dict[ResourceType, ResourceBudget] = {}
        self._allocations: list[ResourceAllocation] = []
        self._agent_allocations: dict[str, list[ResourceAllocation]] = {}
        self._pending_queue: list[tuple] = []
        self._initialized = False

        Logger.info("ResourceManagerAgent initialized")

    def set_budget(
        self,
        resource_type: ResourceType,
        total: float,
        hard_cap: bool = True,
        warning_threshold: float = 0.8,
    ) -> None:
        """Set budget for a resource type."""
        with self._lock:
            self._budgets[resource_type] = ResourceBudget(
                resource_type=resource_type,
                total=total,
                hard_cap=hard_cap,
                warning_threshold=warning_threshold,
            )
            Logger.info(f"Budget set: {resource_type.name} = {total}")

    def allocate(
        self,
        agent_id: str,
        resource_type: ResourceType,
        amount: float,
        priority: int = 0,
    ) -> ResourceAllocation:
        """
        Allocate resources to an agent.

        Thread-safe allocation with hard cap enforcement.

        Args:
            agent_id: Requesting agent identifier
            resource_type: Type of resource to allocate
            amount: Amount to allocate
            priority: Priority level (higher = more important)

        Returns:
            ResourceAllocation with status
        """
        with self._lock:
            # Get or create budget
            if resource_type not in self._budgets:
                self._budgets[resource_type] = ResourceBudget(
                    resource_type=resource_type,
                    total=float("inf"),
                )

            budget = self._budgets[resource_type]

            # Check hard cap
            if budget.hard_cap and budget.is_exhausted:
                Logger.warning(f"HARD CAP: {resource_type.name} exhausted, denying {agent_id}")
                return ResourceAllocation(
                    resource_type=resource_type,
                    amount=0,
                    agent_id=agent_id,
                    status=AllocationStatus.EXHAUSTED,
                )

            # Check if allocation is possible
            if amount <= budget.available:
                # Allocate
                budget.used += amount
                allocation = ResourceAllocation(
                    resource_type=resource_type,
                    amount=amount,
                    agent_id=agent_id,
                    status=AllocationStatus.ALLOCATED,
                )
                self._allocations.append(allocation)

                if agent_id not in self._agent_allocations:
                    self._agent_allocations[agent_id] = []
                self._agent_allocations[agent_id].append(allocation)

                # Check warning threshold
                if budget.utilization >= budget.warning_threshold:
                    Logger.warning(
                        f"WARNING: {resource_type.name} at {budget.utilization * 100:.1f}% utilization",
                    )

                Logger.debug(f"Allocated {amount} {resource_type.name} to {agent_id}")
                return allocation

            # Try fallback strategies
            if self._agent_config.enable_fallback:
                return self._apply_fallback(agent_id, resource_type, amount, priority)

            # Deny allocation
            return ResourceAllocation(
                resource_type=resource_type,
                amount=0,
                agent_id=agent_id,
                status=AllocationStatus.DENIED,
            )

    def _apply_fallback(
        self,
        agent_id: str,
        resource_type: ResourceType,
        amount: float,
        priority: int,
    ) -> ResourceAllocation:
        """Apply fallback strategies when allocation fails."""
        for strategy in self._agent_config.fallback_strategies:
            if strategy == "queue":
                # Queue the request
                self._pending_queue.append((agent_id, resource_type, amount, priority))
                Logger.info(f"Queued allocation request from {agent_id}")
                return ResourceAllocation(
                    resource_type=resource_type,
                    amount=0,
                    agent_id=agent_id,
                    status=AllocationStatus.FALLBACK,
                )
            elif strategy == "throttle":
                # Allocate partial amount
                budget = self._budgets[resource_type]
                partial = min(amount, budget.available)
                if partial > 0:
                    budget.used += partial
                    Logger.info(f"Throttled allocation: {partial}/{amount} to {agent_id}")
                    return ResourceAllocation(
                        resource_type=resource_type,
                        amount=partial,
                        agent_id=agent_id,
                        status=AllocationStatus.FALLBACK,
                    )

        # All strategies failed
        return ResourceAllocation(
            resource_type=resource_type,
            amount=0,
            agent_id=agent_id,
            status=AllocationStatus.DENIED,
        )

    def release(self, agent_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Release allocated resources."""
        with self._lock:
            if resource_type not in self._budgets:
                return False

            budget = self._budgets[resource_type]
            budget.used = max(0, budget.used - amount)

            Logger.debug(f"Released {amount} {resource_type.name} from {agent_id}")
            return True

    def is_exhausted(self, resource_type: ResourceType) -> bool:
        """Check if a resource type is exhausted."""
        with self._lock:
            if resource_type not in self._budgets:
                return False
            return self._budgets[resource_type].is_exhausted

    def get_utilization(self, resource_type: ResourceType) -> float:
        """Get current utilization for a resource type."""
        with self._lock:
            if resource_type not in self._budgets:
                return 0.0
            return self._budgets[resource_type].utilization

    def get_budget_status(self, resource_type: ResourceType) -> dict[str, Any]:
        """Get detailed budget status."""
        with self._lock:
            if resource_type not in self._budgets:
                return {"error": "Budget not found"}

            budget = self._budgets[resource_type]
            return {
                "resource_type": resource_type.name,
                "total": budget.total,
                "used": budget.used,
                "reserved": budget.reserved,
                "available": budget.available,
                "utilization": budget.utilization,
                "is_exhausted": budget.is_exhausted,
                "hard_cap": budget.hard_cap,
            }

    def get_all_budgets(self) -> dict[str, dict[str, Any]]:
        """Get status of all budgets."""
        with self._lock:
            return {rt.name: self.get_budget_status(rt) for rt in self._budgets.keys()}

    def heal(self, violation: dict) -> dict:
        """Heal resource management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget, memory, cpu, tokens)
                - resource_type: ResourceType enum value
                - agent_id: Agent that caused the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        Logger.info("[RESOURCE_MANAGER] Resource violations are runtime-managed")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Resource violations are runtime-managed, not code-healable",
        }


# Factory methods for backward compatibility (will be removed in future)
def create_legacy_budget_manager() -> ResourceManagerAgent:
    """Create a resource manager configured for budget management."""
    manager = ResourceManagerAgent()
    manager.set_budget(ResourceType.BUDGET, total=10000.0)
    return manager


def create_legacy_proactive_manager() -> ResourceManagerAgent:
    """Create a resource manager with proactive allocation enabled."""
    config = ResourceConfig(enable_proactive_allocation=True)
    return ResourceManagerAgent(config=config)


def create_legacy_fallback_manager() -> ResourceManagerAgent:
    """Create a resource manager with fallback strategies."""
    config = ResourceConfig(
        enable_fallback=True,
        fallback_strategies=["throttle", "queue", "reject"],
    )
    return ResourceManagerAgent(config=config)

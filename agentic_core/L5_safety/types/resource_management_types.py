from __future__ import annotations

"""
Resource Management Guardrail - Consolidated Resource Control

Merges:
- CostGovernor
- governor
- control_plane

Composable Rules:
- cost_limits: Cost control and budgeting
- resource_quotas: CPU, memory, token limits
- control_plane: Control plane management
"""


from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResourceType(Enum):
    """Types of managed resources."""

    TOKENS = "tokens"
    API_CALLS = "api_calls"
    MEMORY = "memory"
    CPU = "cpu"
    STORAGE = "storage"
    COST = "cost"


@dataclass
class ResourceQuota:
    """Resource quota definition."""

    resource_type: ResourceType
    limit: float
    used: float = 0.0
    unit: str = ""

    @property
    def remaining(self) -> float:
        return max(0, self.limit - self.used)

    @property
    def usage_percent(self) -> float:
        return (self.used / self.limit * 100) if self.limit > 0 else 0


@dataclass
class ResourceCheckResult:
    """Result of resource check."""

    allowed: bool
    resource_type: ResourceType
    requested: float
    available: float
    message: str = ""


class ResourceManagementGuardrail:
    """
    Consolidated Resource Management Guardrail.

    Provides unified resource control with:
    - Cost limits and budgeting
    - Resource quotas (tokens, API calls, memory)
    - Control plane management
    """

    def __init__(self):
        """Initialize resource management guardrail."""
        self.enabled_rules: list[str] = [
            "cost_limits",
            "resource_quotas",
            "control_plane",
        ]

        # Default quotas
        self.quotas: dict[ResourceType, ResourceQuota] = {
            # guardian: allow-magic-config
            ResourceType.TOKENS: ResourceQuota(
                resource_type=ResourceType.TOKENS,
                limit=1_000_000,
                unit="tokens",
            ),
            # guardian: allow-magic-config
            ResourceType.API_CALLS: ResourceQuota(
                resource_type=ResourceType.API_CALLS,
                limit=1_000,
                unit="calls",
            ),
            # guardian: allow-magic-config
            ResourceType.COST: ResourceQuota(resource_type=ResourceType.COST, limit=100.0, unit="USD"),
            # guardian: allow-magic-config
            ResourceType.MEMORY: ResourceQuota(resource_type=ResourceType.MEMORY, limit=1024, unit="MB"),
        }

        # Cost rates
        self.cost_rates = {
            "gpt-4": 0.03,  # per 1K tokens
            "gpt-3.5-turbo": 0.002,
            "claude-3": 0.015,
            "default": 0.01,
        }

        # Statistics
        self.checks_performed = 0
        self.requests_allowed = 0
        self.requests_denied = 0
        self.total_cost = 0.0

    async def check_resource(self, resource_type: ResourceType, amount: float) -> ResourceCheckResult:
        """
        Check if resource request is allowed.

        Args:
            resource_type: Type of resource
            amount: Amount requested

        Returns:
            ResourceCheckResult
        """
        self.checks_performed += 1

        if "resource_quotas" not in self.enabled_rules:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=float("inf"),
                message="Resource quotas disabled",
            )

        quota = self.quotas.get(resource_type)
        if not quota:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=float("inf"),
                message="No quota defined",
            )

        if amount <= quota.remaining:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=quota.remaining,
                message="Request approved",
            )
        else:
            self.requests_denied += 1
            return ResourceCheckResult(
                allowed=False,
                resource_type=resource_type,
                requested=amount,
                available=quota.remaining,
                message=f"Quota exceeded: requested {amount}, available {quota.remaining}",
            )

    async def consume_resource(self, resource_type: ResourceType, amount: float) -> bool:
        """
        Consume resource from quota.

        Args:
            resource_type: Type of resource
            amount: Amount to consume

        Returns:
            True if consumption successful
        """
        check = await self.check_resource(resource_type, amount)

        if check.allowed:
            quota = self.quotas.get(resource_type)
            if quota:
                quota.used += amount
            return True

        return False

    def calculate_cost(self, model: str, tokens: int) -> float:
        """
        Calculate cost for token usage.

        Args:
            model: Model name
            tokens: Number of tokens

        Returns:
            Cost in USD
        """
        if "cost_limits" not in self.enabled_rules:
            return 0.0

        rate = self.cost_rates.get(model, self.cost_rates["default"])
        cost = (tokens / 1000) * rate
        self.total_cost += cost
        return cost

    async def check_cost_limit(self, estimated_cost: float) -> ResourceCheckResult:
        """
        Check if cost is within limits.

        Args:
            estimated_cost: Estimated cost

        Returns:
            ResourceCheckResult
        """
        return await self.check_resource(ResourceType.COST, estimated_cost)

    def set_quota(self, resource_type: ResourceType, limit: float) -> None:
        """Set quota for resource type."""
        if resource_type in self.quotas:
            self.quotas[resource_type].limit = limit
        else:
            self.quotas[resource_type] = ResourceQuota(resource_type=resource_type, limit=limit)

    def reset_quotas(self) -> None:
        """Reset all quota usage."""
        for quota in self.quotas.values():
            quota.used = 0.0

    def get_quota_status(self) -> dict[str, Any]:
        """Get status of all quotas."""
        return {
            rt.value: {
                "limit": q.limit,
                "used": q.used,
                "remaining": q.remaining,
                "usage_percent": q.usage_percent,
                "unit": q.unit,
            }
            for rt, q in self.quotas.items()
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get resource management statistics."""
        return {
            "checks_performed": self.checks_performed,
            "requests_allowed": self.requests_allowed,
            "requests_denied": self.requests_denied,
            "denial_rate": (self.requests_denied / self.checks_performed * 100)
            if self.checks_performed > 0
            else 0,
            "total_cost": self.total_cost,
            "quota_status": self.get_quota_status(),
        }

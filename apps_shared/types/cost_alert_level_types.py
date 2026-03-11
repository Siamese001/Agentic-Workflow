"""Per-Agent Cost Tracking with Identity Integration.

Phase 4 - Pillar 11 (Cont.): Cost & Optimization
Tracks costs per agent using SPIFFE identity for financial accountability.

Integrates with:
- Phase 3 SPIFFE Identity (Pillar 2)
- Phase 2 observability (Pillar 10)
- Phase 1 Token Budget (Pillar 11)
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class CostAlertLevel(Enum):
    """Cost alert levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CostMetrics:
    """Cost metrics for an agent."""

    agent_id: str
    spiffe_id: str
    total_cost: float
    token_count: int
    request_count: int
    avg_cost_per_request: float
    period_start: float
    period_end: float
    model_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "spiffe_id": self.spiffe_id,
            "total_cost": self.total_cost,
            "token_count": self.token_count,
            "request_count": self.request_count,
            "avg_cost_per_request": self.avg_cost_per_request,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "model_breakdown": self.model_breakdown,
        }


@dataclass
class CostAlert:
    """Cost alert for budget violations."""

    alert_id: str
    agent_id: str
    spiffe_id: str
    level: CostAlertLevel
    message: str
    current_cost: float
    budget_limit: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "spiffe_id": self.spiffe_id,
            "level": self.level.value,
            "message": self.message,
            "current_cost": self.current_cost,
            "budget_limit": self.budget_limit,
            "timestamp": self.timestamp,
        }


class CostTracker:
    """Tracks costs per agent with SPIFFE identity integration.

    Features:
    - Per-agent cost attribution
    - Budget enforcement
    - Cost alerting
    - Model-level breakdown
    - Financial accountability
    """

    def __init__(
        self,
        default_budget_per_agent: float | None = None,
        alert_threshold_percent: float = 0.8,
        enable_logging: bool = True,
    ):
        """Initialize cost tracker.

        Args:
            default_budget_per_agent: Default budget per agent
            alert_threshold_percent: Alert when cost reaches this % of budget
            enable_logging: Enable logging
        """
        self.default_budget_per_agent = default_budget_per_agent
        self.alert_threshold_percent = alert_threshold_percent
        self.enable_logging = enable_logging

        self._agent_costs: dict[str, list[dict[str, Any]]] = {}
        self._agent_budgets: dict[str, float] = {}
        self._alerts: list[CostAlert] = []

        if self.enable_logging:
            logger.info(
                "cost_tracker_initialized",
                extra={
                    "default_budget": default_budget_per_agent,
                    "alert_threshold": alert_threshold_percent,
                },
            )

    def record_cost(
        self,
        agent_id: str,
        spiffe_id: str,
        model_id: str,
        tokens: int,
        cost: float,
    ) -> None:
        """Record cost for an agent.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID for identity
            model_id: Model used
            tokens: Token count
            cost: Cost incurred
        """
        if agent_id not in self._agent_costs:
            self._agent_costs[agent_id] = []

        record = {
            "spiffe_id": spiffe_id,
            "model_id": model_id,
            "tokens": tokens,
            "cost": cost,
            "timestamp": time.time(),
        }

        self._agent_costs[agent_id].append(record)

        # Check budget
        if agent_id in self._agent_budgets:
            self._check_budget(agent_id, spiffe_id)

        if self.enable_logging:
            logger.debug(
                "cost_recorded",
                extra={
                    "agent_id": agent_id,
                    "model_id": model_id,
                    "cost": cost,
                },
            )

    def set_budget(self, agent_id: str, budget: float) -> None:
        """Set budget for an agent.

        Args:
            agent_id: Agent identifier
            budget: Budget amount
        """
        self._agent_budgets[agent_id] = budget

        if self.enable_logging:
            logger.info(
                "budget_set",
                extra={
                    "agent_id": agent_id,
                    "budget": budget,
                },
            )

    def get_metrics(
        self,
        agent_id: str,
        period_hours: int = 24,
    ) -> CostMetrics | None:
        """Get cost metrics for an agent.

        Args:
            agent_id: Agent identifier
            period_hours: Period in hours

        Returns:
            CostMetrics or None
        """
        records = self._agent_costs.get(agent_id, [])

        if not records:
            return None

        # Filter by period
        period_start = time.time() - (period_hours * 3600)
        period_records = [r for r in records if r["timestamp"] >= period_start]

        if not period_records:
            return None

        # Calculate metrics
        total_cost = sum(r["cost"] for r in period_records)
        token_count = sum(r["tokens"] for r in period_records)
        request_count = len(period_records)
        avg_cost = total_cost / request_count if request_count > 0 else 0.0

        # Model breakdown
        model_breakdown: dict[str, float] = {}
        for record in period_records:
            model_id = record["model_id"]
            model_breakdown[model_id] = model_breakdown.get(model_id, 0.0) + record["cost"]

        # Get SPIFFE ID from most recent record
        spiffe_id = period_records[-1]["spiffe_id"]

        metrics = CostMetrics(
            agent_id=agent_id,
            spiffe_id=spiffe_id,
            total_cost=total_cost,
            token_count=token_count,
            request_count=request_count,
            avg_cost_per_request=avg_cost,
            period_start=period_start,
            period_end=time.time(),
            model_breakdown=model_breakdown,
        )

        return metrics

    def get_all_metrics(
        self,
        period_hours: int = 24,
    ) -> list[CostMetrics]:
        """Get metrics for all agents.

        Args:
            period_hours: Period in hours

        Returns:
            List of CostMetrics
        """
        all_metrics = []

        for agent_id in self._agent_costs.keys():
            metrics = self.get_metrics(agent_id, period_hours)
            if metrics:
                all_metrics.append(metrics)

        return all_metrics

    def get_alerts(
        self,
        agent_id: str | None = None,
        level: CostAlertLevel | None = None,
    ) -> list[CostAlert]:
        """Get cost alerts.

        Args:
            agent_id: Optional agent ID filter
            level: Optional level filter

        Returns:
            List of CostAlert
        """
        alerts = self._alerts

        if agent_id:
            alerts = [a for a in alerts if a.agent_id == agent_id]

        if level:
            alerts = [a for a in alerts if a.level == level]

        return alerts

    def _check_budget(self, agent_id: str, spiffe_id: str) -> None:
        """Check if agent is within budget.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID
        """
        budget = self._agent_budgets.get(agent_id)
        if not budget:
            return

        metrics = self.get_metrics(agent_id)
        if not metrics:
            return

        current_cost = metrics.total_cost
        usage_percent = current_cost / budget

        # Check thresholds
        if usage_percent >= 1.0:
            self._create_alert(
                agent_id=agent_id,
                spiffe_id=spiffe_id,
                level=CostAlertLevel.CRITICAL,
                message=f"Budget exceeded: ${current_cost:.2f} / ${budget:.2f}",
                current_cost=current_cost,
                budget_limit=budget,
            )
        elif usage_percent >= self.alert_threshold_percent:
            self._create_alert(
                agent_id=agent_id,
                spiffe_id=spiffe_id,
                level=CostAlertLevel.WARNING,
                message=f"Budget at {usage_percent:.1%}: ${current_cost:.2f} / ${budget:.2f}",
                current_cost=current_cost,
                budget_limit=budget,
            )

    def _create_alert(
        self,
        agent_id: str,
        spiffe_id: str,
        level: CostAlertLevel,
        message: str,
        current_cost: float,
        budget_limit: float,
    ) -> None:
        """Create cost alert.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID
            level: Alert level
            message: Alert message
            current_cost: Current cost
            budget_limit: Budget limit
        """
        alert = CostAlert(
            alert_id=f"cost_alert_{agent_id}_{int(time.time())}",
            agent_id=agent_id,
            spiffe_id=spiffe_id,
            level=level,
            message=message,
            current_cost=current_cost,
            budget_limit=budget_limit,
        )

        self._alerts.append(alert)

        # Keep only recent alerts (last 100)
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]

        if self.enable_logging:
            logger.warning(
                "cost_alert_triggered",
                extra={
                    "agent_id": agent_id,
                    "level": level.value,
                    "current_cost": current_cost,
                    "budget": budget_limit,
                },
            )


def create_cost_tracker(
    default_budget_per_agent: float | None = None,
) -> CostTracker:
    """Factory function to create cost tracker.

    Args:
        default_budget_per_agent: Default budget per agent

    Returns:
        CostTracker instance
    """
    return CostTracker(default_budget_per_agent=default_budget_per_agent)

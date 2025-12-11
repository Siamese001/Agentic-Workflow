"""Safety Cost Tracker - Tracks and manages safety-related costs.

This module provides cost tracking for safety operations,
including policy enforcement, filter applications, and compliance checks.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CostType(Enum):
    """Types of safety costs."""
    POLICY_CHECK = "policy_check"
    FILTER_APPLICATION = "filter_application"
    ETHICS_VALIDATION = "ethics_validation"
    COMPLIANCE_CHECK = "compliance_check"
    VIOLATION_HANDLING = "violation_handling"
    API_CALL = "api_call"
    STORAGE = "storage"
    COMPUTE = "compute"


@dataclass
class CostRecord:
    """Record of a safety cost."""
    cost_type: CostType
    amount: float
    currency: str = "USD"
    operation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostBudget:
    """Budget definition for safety costs."""
    budget_type: CostType
    limit: float
    period: str  # daily, weekly, monthly
    current_usage: float = 0.0
    alert_threshold: float = 0.8
    currency: str = "USD"


@dataclass
class CostSummary:
    """Summary of safety costs."""
    total_cost: float
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    period_costs: Dict[str, Dict[str, float]] = field(default_factory=dict)
    budget_status: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    forecast: Optional[Dict[str, float]] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyCostConfig:
    """Configuration for safety cost tracking."""
    enable_budget_tracking: bool = True
    default_currency: str = "USD"
    cost_precision: int = 4
    forecast_days: int = 30
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "daily": 0.8,
        "weekly": 0.7,
        "monthly": 0.9
    })
    log_level: str = "INFO"


class SafetyCostTracker:
    """Main class for tracking safety costs."""

    def __init__(self, config: Optional[SafetyCostConfig] = None):
        self.config = config or SafetyCostConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._cost_records: List[CostRecord] = []
        self._budgets: Dict[str, CostBudget] = {}
        self._load_default_budgets()

    def track_cost(self, cost_record: CostRecord) -> bool:
        """Track a new safety cost.
        
        Args:
            cost_record: Cost record to track
            
        Returns:
            bool: True if cost was tracked successfully
        """
        try:
            self.logger.info(f"Tracking safety cost: {cost_record.cost_type.value} = {cost_record.amount} {cost_record.currency}")
            
            # Add cost record
            self._cost_records.append(cost_record)
            
            # Update budget usage
            if self.config.enable_budget_tracking:
                self._update_budget_usage(cost_record)
            
            # Check budget alerts
            if self.config.enable_budget_tracking:
                self._check_budget_alerts(cost_record.cost_type)
            
            # Clean old records
            self._cleanup_old_records()
            
            self.logger.info(f"Safety cost tracked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track safety cost: {str(e)}")
            return False

    def get_cost_summary(self, period: str = "total") -> CostSummary:
        """Get cost summary for a period.
        
        Args:
            period: Period for summary (total, daily, weekly, monthly)
            
        Returns:
            CostSummary: Cost summary
        """
        try:
            summary = CostSummary(total_cost=0.0)
            
            # Filter records by period
            filtered_records = self._filter_records_by_period(self._cost_records, period)
            
            # Calculate total cost
            summary.total_cost = sum(r.amount for r in filtered_records)
            summary.total_cost = round(summary.total_cost, self.config.cost_precision)
            
            # Calculate cost breakdown by type
            for record in filtered_records:
                cost_type = record.cost_type.value
                summary.cost_breakdown[cost_type] = summary.cost_breakdown.get(cost_type, 0.0) + record.amount
            
            # Round breakdown costs
            for key in summary.cost_breakdown:
                summary.cost_breakdown[key] = round(summary.cost_breakdown[key], self.config.cost_precision)
            
            # Calculate period costs
            if period != "total":
                summary.period_costs = self._calculate_period_costs(filtered_records)
            
            # Check budget status
            if self.config.enable_budget_tracking:
                summary.budget_status = self._get_budget_status()
            
            # Generate forecast
            summary.forecast = self._generate_forecast(filtered_records)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get cost summary: {str(e)}")
            return CostSummary(total_cost=0.0, generated_at=datetime.utcnow())

    def set_budget(self, budget: CostBudget) -> bool:
        """Set a cost budget.
        
        Args:
            budget: Budget to set
            
        Returns:
            bool: True if budget was set successfully
        """
        try:
            self.logger.info(f"Setting budget: {budget.budget_type.value} = {budget.limit} {budget.currency}/{budget.period}")
            
            budget_key = f"{budget.budget_type.value}_{budget.period}"
            self._budgets[budget_key] = budget
            
            # Update current usage
            budget.current_usage = self._calculate_current_usage(budget.budget_type, budget.period)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set budget: {str(e)}")
            return False

    def check_budget_status(self, cost_type: CostType, period: str) -> Dict[str, Any]:
        """Check budget status for a cost type and period.
        
        Args:
            cost_type: Type of cost to check
            period: Period to check
            
        Returns:
            Dict: Budget status information
        """
        try:
            budget_key = f"{cost_type.value}_{period}"
            budget = self._budgets.get(budget_key)
            
            if not budget:
                return {"status": "no_budget", "message": f"No budget set for {cost_type.value} {period}"}
            
            current_usage = self._calculate_current_usage(cost_type, period)
            usage_percentage = current_usage / budget.limit if budget.limit > 0 else 0
            
            status = {
                "budget_limit": budget.limit,
                "current_usage": round(current_usage, self.config.cost_precision),
                "usage_percentage": round(usage_percentage * 100, 2),
                "remaining": round(budget.limit - current_usage, self.config.cost_precision),
                "alert_threshold": round(budget.alert_threshold * 100, 2)
            }
            
            # Determine status level
            if usage_percentage >= 1.0:
                status["status"] = "exceeded"
                status["alert"] = True
            elif usage_percentage >= budget.alert_threshold:
                status["status"] = "warning"
                status["alert"] = True
            else:
                status["status"] = "ok"
                status["alert"] = False
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to check budget status: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _load_default_budgets(self) -> None:
        """Load default budgets."""
        # Daily budgets
        self._budgets["policy_check_daily"] = CostBudget(
            cost_type=CostType.POLICY_CHECK,
            limit=10.0,
            period="daily",
            alert_threshold=0.8
        )
        
        self._budgets["filter_application_daily"] = CostBudget(
            cost_type=CostType.FILTER_APPLICATION,
            limit=5.0,
            period="daily",
            alert_threshold=0.8
        )
        
        # Weekly budgets
        self._budgets["ethics_validation_weekly"] = CostBudget(
            cost_type=CostType.ETHICS_VALIDATION,
            limit=50.0,
            period="weekly",
            alert_threshold=0.7
        )
        
        # Monthly budgets
        self._budgets["compliance_check_monthly"] = CostBudget(
            cost_type=CostType.COMPLIANCE_CHECK,
            limit=100.0,
            period="monthly",
            alert_threshold=0.9
        )

    def _update_budget_usage(self, cost_record: CostRecord) -> None:
        """Update budget usage for all relevant budgets."""
        cost_type = cost_record.cost_type
        
        for period in ["daily", "weekly", "monthly"]:
            budget_key = f"{cost_type.value}_{period}"
            budget = self._budgets.get(budget_key)
            
            if budget:
                budget.current_usage = self._calculate_current_usage(cost_type, period)

    def _calculate_current_usage(self, cost_type: CostType, period: str) -> float:
        """Calculate current usage for a cost type and period."""
        filtered_records = self._filter_records_by_period(
            [r for r in self._cost_records if r.cost_type == cost_type],
            period
        )
        return sum(r.amount for r in filtered_records)

    def _filter_records_by_period(self, records: List[CostRecord], period: str) -> List[CostRecord]:
        """Filter cost records by period."""
        if period == "total":
            return records
        
        now = datetime.utcnow()
        
        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return records
        
        return [r for r in records if r.timestamp >= start_date]

    def _check_budget_alerts(self, cost_type: CostType) -> None:
        """Check and trigger budget alerts."""
        for period in ["daily", "weekly", "monthly"]:
            status = self.check_budget_status(cost_type, period)
            
            if status.get("alert"):
                self.logger.warning(
                    f"Budget alert for {cost_type.value} {period}: "
                    f"{status['usage_percentage']}% used ({status['current_usage']}/{status['budget_limit']})"
                )

    def _calculate_period_costs(self, records: List[CostRecord]) -> Dict[str, Dict[str, float]]:
        """Calculate costs by sub-periods."""
        period_costs = {}
        
        # Group by date
        daily_costs = {}
        for record in records:
            date_key = record.timestamp.date().isoformat()
            if date_key not in daily_costs:
                daily_costs[date_key] = {}
            
            cost_type = record.cost_type.value
            daily_costs[date_key][cost_type] = daily_costs[date_key].get(cost_type, 0.0) + record.amount
        
        # Round costs
        for date in daily_costs:
            for cost_type in daily_costs[date]:
                daily_costs[date][cost_type] = round(daily_costs[date][cost_type], self.config.cost_precision)
        
        period_costs["daily"] = daily_costs
        return period_costs

    def _get_budget_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all budgets."""
        budget_status = {}
        
        for budget_key, budget in self._budgets.items():
            cost_type, period = budget_key.split("_")
            status = self.check_budget_status(CostType(cost_type), period)
            budget_status[budget_key] = status
        
        return budget_status

    def _generate_forecast(self, records: List[CostRecord]) -> Optional[Dict[str, float]]:
        """Generate cost forecast."""
        if len(records) < 7:
            return None
        
        try:
            # Simple linear forecast based on recent trend
            recent_costs = []
            now = datetime.utcnow()
            
            # Get daily costs for last 7 days
            for i in range(7):
                date = now - timedelta(days=i)
                date_records = [r for r in records if r.timestamp.date() == date.date()]
                daily_cost = sum(r.amount for r in date_records)
                recent_costs.append(daily_cost)
            
            # Calculate average daily cost
            avg_daily_cost = sum(recent_costs) / len(recent_costs)
            
            # Generate forecast
            forecast = {
                "daily_forecast": round(avg_daily_cost, self.config.cost_precision),
                "weekly_forecast": round(avg_daily_cost * 7, self.config.cost_precision),
                "monthly_forecast": round(avg_daily_cost * 30, self.config.cost_precision)
            }
            
            return forecast
            
        except Exception as e:
            self.logger.warning(f"Failed to generate forecast: {str(e)}")
            return None

    def _cleanup_old_records(self) -> None:
        """Clean up old cost records."""
        # Keep records for 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        original_count = len(self._cost_records)
        
        self._cost_records = [r for r in self._cost_records if r.timestamp >= cutoff_date]
        
        if len(self._cost_records) < original_count:
            self.logger.info(f"Cleaned up {original_count - len(self._cost_records)} old cost records")


# Factory function for easy instantiation
def create_safety_cost_tracker(
    enable_budget_tracking: bool = True,
    default_currency: str = "USD",
    forecast_days: int = 30,
    **kwargs
) -> SafetyCostTracker:
    """Create a configured safety cost tracker."""
    config = SafetyCostConfig(
        enable_budget_tracking=enable_budget_tracking,
        default_currency=default_currency,
        forecast_days=forecast_days,
        **kwargs
    )
    return SafetyCostTracker(config)


# Convenience function for direct usage
def track_safety_cost(
    cost_type: str,
    amount: float,
    operation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Track a safety cost.
    
    Args:
        cost_type: Type of cost
        amount: Cost amount
        operation_id: Optional operation ID
        metadata: Optional metadata
        config: Optional tracker configuration
        
    Returns:
        bool: True if cost was tracked successfully
    """
    # Create tracker and track
    tracker_config = SafetyCostConfig(**config or {})
    tracker = SafetyCostTracker(tracker_config)
    
    cost_record = CostRecord(
        cost_type=CostType(cost_type),
        amount=amount,
        operation_id=operation_id,
        metadata=metadata or {}
    )
    
    return tracker.track_cost(cost_record)

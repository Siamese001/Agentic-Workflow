"""Safety Budget Enforcer - Enforces safety operation budgets and limits.

This module provides budget enforcement for safety operations,
including cost limits, usage quotas, and resource constraints.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class BudgetType(Enum):
    """Types of safety budgets."""
    COST_BUDGET = "cost_budget"
    USAGE_BUDGET = "usage_budget"
    OPERATION_BUDGET = "operation_budget"
    RESOURCE_BUDGET = "resource_budget"
    TIME_BUDGET = "time_budget"


class EnforcementAction(Enum):
    """Actions for budget violations."""
    BLOCK = "block"
    WARN = "warn"
    THROTTLE = "throttle"
    ESCALATE = "escalate"
    LOG = "log"


@dataclass
class BudgetLimit:
    """Definition of a budget limit."""
    budget_type: BudgetType
    limit_value: float
    period: str  # per_second, per_minute, hourly, daily, weekly, monthly
    current_usage: float = 0.0
    reset_time: Optional[datetime] = None
    enforcement_action: EnforcementAction = EnforcementAction.WARN
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetViolation:
    """Record of a budget violation."""
    budget_type: BudgetType
    limit_value: float
    actual_value: float
    period: str
    action_taken: EnforcementAction
    operation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BudgetEnforcementResult:
    """Result of budget enforcement."""
    allowed: bool
    budget_id: str
    remaining_budget: float
    usage_percentage: float
    violation: Optional[BudgetViolation] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyBudgetConfig:
    """Configuration for safety budget enforcement."""
    strict_mode: bool = False
    default_action: EnforcementAction = EnforcementAction.WARN
    enable_auto_reset: bool = True
    reset_buffer_minutes: int = 5
    escalation_threshold: float = 1.5  # 150% of budget
    custom_handlers: Dict[str, Callable] = field(default_factory=dict)
    log_level: str = "INFO"


class SafetyBudgetEnforcer:
    """Main class for enforcing safety budgets."""

    def __init__(self, config: Optional[SafetyBudgetConfig] = None):
        self.config = config or SafetyBudgetConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._budgets: Dict[str, BudgetLimit] = {}
        self._usage_history: List[Dict[str, Any]] = []
        self._load_default_budgets()

    def enforce_budget(self, operation: Dict[str, Any]) -> BudgetEnforcementResult:
        """Enforce budget limits on an operation.
        
        Args:
            operation: Operation details with resource requirements
            
        Returns:
            BudgetEnforcementResult: Budget enforcement result
        """
        try:
            self.logger.info(f"Enforcing safety budget for operation: {operation.get('id', 'unknown')}")
            
            operation_id = operation.get("id", "unknown")
            results = []
            
            # Check all applicable budgets
            for budget_id, budget in self._budgets.items():
                result = self._check_budget_limit(budget_id, budget, operation)
                results.append(result)
            
            # Find the most restrictive result
            if results:
                # If any budget blocks, operation is blocked
                blocked_results = [r for r in results if not r.allowed]
                if blocked_results:
                    # Return the first blocked result
                    return blocked_results[0]
                
                # Otherwise, return the result with highest usage percentage
                highest_usage = max(results, key=lambda x: x.usage_percentage)
                return highest_usage
            
            # No budgets configured - allow by default
            return BudgetEnforcementResult(
                allowed=True,
                budget_id="none",
                remaining_budget=float('inf'),
                usage_percentage=0.0,
                metadata={"no_budgets": True}
            )
            
        except Exception as e:
            self.logger.error(f"Budget enforcement failed: {str(e)}")
            return BudgetEnforcementResult(
                allowed=False,
                budget_id="error",
                remaining_budget=0.0,
                usage_percentage=100.0,
                metadata={"error": str(e)}
            )

    def add_budget_limit(self, budget_id: str, budget: BudgetLimit) -> bool:
        """Add a new budget limit.
        
        Args:
            budget_id: Unique identifier for the budget
            budget: Budget limit definition
            
        Returns:
            bool: True if budget was added successfully
        """
        try:
            self.logger.info(f"Adding budget limit: {budget_id}")
            
            # Set initial reset time if not set
            if not budget.reset_time:
                budget.reset_time = self._calculate_next_reset(budget.period)
            
            self._budgets[budget_id] = budget
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add budget limit: {str(e)}")
            return False

    def update_usage(self, budget_id: str, usage_amount: float, operation_id: Optional[str] = None) -> bool:
        """Update usage for a specific budget.
        
        Args:
            budget_id: Budget to update
            usage_amount: Amount of usage to add
            operation_id: Optional operation ID
            
        Returns:
            bool: True if update was successful
        """
        try:
            budget = self._budgets.get(budget_id)
            if not budget:
                self.logger.warning(f"Budget not found: {budget_id}")
                return False
            
            # Check if budget needs reset
            if self.config.enable_auto_reset and datetime.utcnow() >= budget.reset_time:
                self._reset_budget(budget)
            
            # Update usage
            budget.current_usage += usage_amount
            
            # Record usage
            self._usage_history.append({
                "budget_id": budget_id,
                "usage_amount": usage_amount,
                "operation_id": operation_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.debug(f"Updated usage for {budget_id}: {budget.current_usage}/{budget.limit_value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update usage: {str(e)}")
            return False

    def get_budget_status(self, budget_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of budgets.
        
        Args:
            budget_id: Specific budget ID or None for all
            
        Returns:
            Dict: Budget status information
        """
        try:
            if budget_id:
                budgets = {budget_id: self._budgets.get(budget_id)}
            else:
                budgets = self._budgets
            
            status = {}
            
            for bid, budget in budgets.items():
                if not budget:
                    continue
                
                usage_percentage = (budget.current_usage / budget.limit_value * 100) if budget.limit_value > 0 else 0
                remaining = budget.limit_value - budget.current_usage
                
                status[bid] = {
                    "budget_type": budget.budget_type.value,
                    "limit": budget.limit_value,
                    "current_usage": budget.current_usage,
                    "remaining": remaining,
                    "usage_percentage": round(usage_percentage, 2),
                    "period": budget.period,
                    "reset_time": budget.reset_time.isoformat() if budget.reset_time else None,
                    "enforcement_action": budget.enforcement_action.value
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get budget status: {str(e)}")
            return {"error": str(e)}

    def reset_budget(self, budget_id: str) -> bool:
        """Manually reset a budget.
        
        Args:
            budget_id: Budget to reset
            
        Returns:
            bool: True if reset was successful
        """
        try:
            budget = self._budgets.get(budget_id)
            if not budget:
                self.logger.warning(f"Budget not found: {budget_id}")
                return False
            
            self._reset_budget(budget)
            self.logger.info(f"Budget {budget_id} reset manually")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset budget: {str(e)}")
            return False

    def _check_budget_limit(self, budget_id: str, budget: BudgetLimit, operation: Dict[str, Any]) -> BudgetEnforcementResult:
        """Check if operation exceeds budget limit."""
        try:
            # Check if budget needs reset
            if self.config.enable_auto_reset and datetime.utcnow() >= budget.reset_time:
                self._reset_budget(budget)
            
            # Get operation cost/usage
            operation_cost = self._extract_operation_cost(budget.budget_type, operation)
            
            # Calculate projected usage
            projected_usage = budget.current_usage + operation_cost
            
            # Calculate percentages
            current_percentage = (budget.current_usage / budget.limit_value * 100) if budget.limit_value > 0 else 0
            projected_percentage = (projected_usage / budget.limit_value * 100) if budget.limit_value > 0 else 0
            
            remaining_budget = budget.limit_value - budget.current_usage
            
            # Check for violation
            if projected_usage > budget.limit_value:
                # Handle violation
                violation = BudgetViolation(
                    budget_type=budget.budget_type,
                    limit_value=budget.limit_value,
                    actual_value=projected_usage,
                    period=budget.period,
                    action_taken=budget.enforcement_action,
                    operation_id=operation.get("id")
                )
                
                # Take enforcement action
                if budget.enforcement_action == EnforcementAction.BLOCK:
                    return BudgetEnforcementResult(
                        allowed=False,
                        budget_id=budget_id,
                        remaining_budget=remaining_budget,
                        usage_percentage=projected_percentage,
                        violation=violation,
                        metadata={"blocked_by": budget_id}
                    )
                elif budget.enforcement_action == EnforcementAction.WARN:
                    return BudgetEnforcementResult(
                        allowed=True,
                        budget_id=budget_id,
                        remaining_budget=remaining_budget,
                        usage_percentage=projected_percentage,
                        violation=violation,
                        warnings=[f"Budget warning: {projected_percentage:.1f}% used"],
                        metadata={"warning": True}
                    )
                elif budget.enforcement_action == EnforcementAction.THROTTLE:
                    return BudgetEnforcementResult(
                        allowed=True,
                        budget_id=budget_id,
                        remaining_budget=0.0,
                        usage_percentage=100.0,
                        violation=violation,
                        metadata={"throttled": True}
                    )
                elif budget.enforcement_action == EnforcementAction.ESCALATE:
                    self._handle_escalation(budget_id, budget, violation, operation)
                    return BudgetEnforcementResult(
                        allowed=True,
                        budget_id=budget_id,
                        remaining_budget=remaining_budget,
                        usage_percentage=projected_percentage,
                        violation=violation,
                        metadata={"escalated": True}
                    )
            
            # Check for warnings
            warnings = []
            if current_percentage >= 80:
                warnings.append(f"Budget usage high: {current_percentage:.1f}%")
            
            return BudgetEnforcementResult(
                allowed=True,
                budget_id=budget_id,
                remaining_budget=remaining_budget,
                usage_percentage=current_percentage,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Failed to check budget limit: {str(e)}")
            return BudgetEnforcementResult(
                allowed=False,
                budget_id=budget_id,
                remaining_budget=0.0,
                usage_percentage=100.0,
                metadata={"error": str(e)}
            )

    def _extract_operation_cost(self, budget_type: BudgetType, operation: Dict[str, Any]) -> float:
        """Extract cost/usage from operation based on budget type."""
        if budget_type == BudgetType.COST_BUDGET:
            return float(operation.get("cost", 0.0))
        elif budget_type == BudgetType.USAGE_BUDGET:
            return float(operation.get("usage_units", 0.0))
        elif budget_type == BudgetType.OPERATION_BUDGET:
            return 1.0  # Each operation counts as 1
        elif budget_type == BudgetType.RESOURCE_BUDGET:
            return float(operation.get("resource_units", 0.0))
        elif budget_type == BudgetType.TIME_BUDGET:
            return float(operation.get("execution_time_seconds", 0.0))
        
        return 0.0

    def _calculate_next_reset(self, period: str) -> datetime:
        """Calculate next reset time for a period."""
        now = datetime.utcnow()
        
        if period == "per_second":
            return now + timedelta(seconds=1)
        elif period == "per_minute":
            return now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif period == "hourly":
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif period == "daily":
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == "weekly":
            days_until_monday = (7 - now.weekday()) % 7 or 7
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        elif period == "monthly":
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return now + timedelta(hours=1)

    def _reset_budget(self, budget: BudgetLimit) -> None:
        """Reset a budget's usage."""
        budget.current_usage = 0.0
        budget.reset_time = self._calculate_next_reset(budget.period)
        self.logger.debug(f"Reset budget: {budget.budget_type.value}")

    def _handle_escalation(self, budget_id: str, budget: BudgetLimit, violation: BudgetViolation, operation: Dict[str, Any]) -> None:
        """Handle budget violation escalation."""
        self.logger.warning(
            f"Budget escalation triggered for {budget_id}: "
            f"usage {violation.actual_value} exceeds limit {violation.limit_value}"
        )
        
        # Call custom handler if configured
        handler = self.config.custom_handlers.get(budget_id)
        if handler:
            try:
                handler(budget, violation, operation)
            except Exception as e:
                self.logger.error(f"Custom escalation handler failed: {str(e)}")

    def _load_default_budgets(self) -> None:
        """Load default budget limits."""
        # Cost budget - $10 per hour
        self.add_budget_limit(
            "cost_hourly",
            BudgetLimit(
                budget_type=BudgetType.COST_BUDGET,
                limit_value=10.0,
                period="hourly",
                enforcement_action=EnforcementAction.WARN
            )
        )
        
        # Operation budget - 1000 operations per minute
        self.add_budget_limit(
            "operations_per_minute",
            BudgetLimit(
                budget_type=BudgetType.OPERATION_BUDGET,
                limit_value=1000.0,
                period="per_minute",
                enforcement_action=EnforcementAction.THROTTLE
            )
        )
        
        # Usage budget - 10000 units per day
        self.add_budget_limit(
            "usage_daily",
            BudgetLimit(
                budget_type=BudgetType.USAGE_BUDGET,
                limit_value=10000.0,
                period="daily",
                enforcement_action=EnforcementAction.WARN
            )
        )


# Factory function for easy instantiation
def create_safety_budget_enforcer(
    strict_mode: bool = False,
    default_action: str = "warn",
    enable_auto_reset: bool = True,
    **kwargs
) -> SafetyBudgetEnforcer:
    """Create a configured safety budget enforcer."""
    config = SafetyBudgetConfig(
        strict_mode=strict_mode,
        default_action=EnforcementAction(default_action),
        enable_auto_reset=enable_auto_reset,
        **kwargs
    )
    return SafetyBudgetEnforcer(config)


# Convenience function for direct usage
def enforce_safety_budget(
    operation: Dict[str, Any],
    strict_mode: bool = False,
    budget_limits: Optional[Dict[str, Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enforce safety budget on an operation.
    
    Args:
        operation: Operation details
        strict_mode: Whether to use strict enforcement
        budget_limits: Optional budget limits to apply
        config: Optional enforcer configuration
        
    Returns:
        Dict: Budget enforcement result
    """
    # Create enforcer
    enforcer_config = SafetyBudgetConfig(
        strict_mode=strict_mode,
        **config or {}
    )
    enforcer = SafetyBudgetEnforcer(enforcer_config)
    
    # Add custom budgets if provided
    if budget_limits:
        for budget_id, budget_config in budget_limits.items():
            budget = BudgetLimit(
                budget_type=BudgetType(budget_config["budget_type"]),
                limit_value=budget_config["limit_value"],
                period=budget_config["period"],
                enforcement_action=EnforcementAction(budget_config.get("enforcement_action", "warn"))
            )
            enforcer.add_budget_limit(budget_id, budget)
    
    # Enforce budget
    result = enforcer.enforce_budget(operation)
    
    # Convert result to dict
    return {
        "allowed": result.allowed,
        "budget_id": result.budget_id,
        "remaining_budget": result.remaining_budget,
        "usage_percentage": result.usage_percentage,
        "violation": {
            "budget_type": result.violation.budget_type.value,
            "limit_value": result.violation.limit_value,
            "actual_value": result.violation.actual_value,
            "period": result.violation.period,
            "action_taken": result.violation.action_taken.value,
            "timestamp": result.violation.timestamp.isoformat()
        } if result.violation else None,
        "warnings": result.warnings,
        "metadata": result.metadata
    }

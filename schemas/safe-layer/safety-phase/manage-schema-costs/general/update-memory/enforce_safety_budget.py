"""
Schema definitions for safety budget enforcement and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class BudgetType(Enum):
    """Safety budget management types."""
    COMPUTATIONAL = "computational"
    FINANCIAL = "financial"
    TEMPORAL = "temporal"
    RESOURCE = "resource"


class EnforcementAction(Enum):
    """Budget enforcement actions."""
    THROTTLE = "throttle"
    BLOCK = "block"
    ESCALATE = "escalate"
    NOTIFY = "notify"


@dataclass
class SafetyBudget:
    """Schema for individual safety budget."""
    budget_id: str
    budget_type: BudgetType
    allocated_amount: Union[int, float]
    used_amount: Union[int, float]
    remaining_amount: Union[int, float]


@dataclass
class BudgetEnforcement:
    """Schema for budget enforcement context."""
    enforcement_id: str
    target_schema_id: str
    applied_budgets: List[SafetyBudget]
    enforcement_action: EnforcementAction
    enforcement_timestamp: str


@dataclass
class BudgetEnforcementResult:
    """Schema for budget enforcement results."""
    result_id: str
    enforcement: BudgetEnforcement
    violations_detected: List[str]
    actions_taken: List[EnforcementAction]
    enforcement_successful: bool
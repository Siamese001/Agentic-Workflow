"""
Schema definitions for schema budget management and updates.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class BudgetType(Enum):
    """Schema budget management types."""
    COMPUTATIONAL = "computational"
    FINANCIAL = "financial"
    TEMPORAL = "temporal"
    RESOURCE = "resource"


class UpdateFrequency(Enum):
    """Budget update frequency."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class BudgetAllocation:
    """Schema for individual budget allocation."""
    allocation_id: str
    budget_type: BudgetType
    allocated_amount: Union[int, float]
    used_amount: Union[int, float]
    remaining_amount: Union[int, float]


@dataclass
class BudgetUpdate:
    """Schema for budget update configuration."""
    update_id: str
    target_schema_id: str
    update_frequency: UpdateFrequency
    allocations: List[BudgetAllocation]
    auto_adjust: bool = False


@dataclass
class BudgetUpdateResult:
    """Schema for budget update results."""
    result_id: str
    update: BudgetUpdate
    updated_allocations: List[BudgetAllocation]
    savings_achieved: Union[int, float]
    update_timestamp: str
"""
Schema definitions for safety usage management and updates.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import List, Union
from enum import Enum


class UsageType(Enum):
    """Safety usage management types."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    API_CALLS = "api_calls"


class UpdateFrequency(Enum):
    """Usage update frequency."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class UsageAllocation:
    """Schema for individual usage allocation."""
    allocation_id: str
    usage_type: UsageType
    allocated_amount: Union[int, float]
    used_amount: Union[int, float]
    remaining_amount: Union[int, float]


@dataclass
class UsageUpdate:
    """Schema for usage update configuration."""
    update_id: str
    target_schema_id: str
    update_frequency: UpdateFrequency
    allocations: List[UsageAllocation]
    auto_adjust: bool = False


@dataclass
class UsageUpdateResult:
    """Schema for usage update results."""
    result_id: str
    update: UsageUpdate
    updated_allocations: List[UsageAllocation]
    efficiency_gained: Union[int, float]
    update_timestamp: str
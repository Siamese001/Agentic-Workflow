"""
Schema definitions for orchestration-level schema payload preparation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class PayloadType(Enum):
    """Orchestration payload types."""
    WORKFLOW = "workflow"
    TASK = "task"
    EVENT = "event"
    COMMAND = "command"


class PreparationStrategy(Enum):
    """Payload preparation strategies."""
    IMMEDIATE = "immediate"
    BATCHED = "batched"
    STREAMING = "streaming"
    LAZY = "lazy"


@dataclass
class PayloadSpecification:
    """Schema for payload specification."""
    payload_id: str
    payload_type: PayloadType
    target_system: str
    priority: str
    delivery_mode: str


@dataclass
class PayloadPreparationConfig:
    """Schema for payload preparation configuration."""
    strategy: PreparationStrategy
    compression_enabled: bool = False
    encryption_enabled: bool = False
    validation_required: bool = True
    retry_policy: Optional[Dict[str, Any]] = None


@dataclass
class PreparedPayload:
    """Schema for prepared orchestration payload."""
    payload_id: str
    specification: PayloadSpecification
    prepared_data: Dict[str, Any]
    metadata: Dict[str, str]
    preparation_timestamp: str

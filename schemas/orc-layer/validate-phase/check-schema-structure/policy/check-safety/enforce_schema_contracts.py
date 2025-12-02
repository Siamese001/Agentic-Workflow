"""
Schema definitions for orchestration-level schema contract enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ContractType(Enum):
    """Orchestration contract types."""
    SERVICE_LEVEL = "service_level"
    WORKFLOW = "workflow"
    RESOURCE = "resource"
    SECURITY = "security"


class EnforcementLevel(Enum):
    """Contract enforcement levels."""
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKING = "blocking"
    ESCALATION = "escalation"


@dataclass
class OrchestrationContract:
    """Schema for orchestration contract."""
    contract_id: str
    contract_type: ContractType
    parties: List[str]
    terms: List[Dict[str, Any]]
    enforcement_level: EnforcementLevel


@dataclass
class ContractEnforcementConfig:
    enforcement_level: EnforcementLevel
    notification_channels: List[str]
    automatic_violation_detection: bool = True
    escalation_enabled: bool = False
    """Schema for contract enforcement configuration."""


@dataclass
class ContractEnforcementResult:
    """Schema for contract enforcement results."""
    enforcement_id: str
    configuration: ContractEnforcementConfig
    violations: List[Dict[str, Any]]
    actions_taken: List[str]
    enforcement_timestamp: str

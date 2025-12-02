"""
Schema definitions for execution contract enforcement and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ContractType(Enum):
    """Execution contract types."""
    SERVICE_LEVEL = "service_level"
    PERFORMANCE = "performance"
    SECURITY = "security"
    RESOURCE = "resource"


class EnforcementLevel(Enum):
    """Contract enforcement levels."""
    STRICT = "strict"
    MODERATE = "moderate"
    ADVISORY = "advisory"
    MONITORING = "monitoring"


@dataclass
class ExecutionContract:
    """Schema for individual execution contract."""
    contract_id: str
    contract_type: ContractType
    contract_terms: List[Dict[str, Any]]
    enforcement_level: EnforcementLevel
    parties: List[str]


@dataclass
class ContractEnforcement:
    """Schema for contract enforcement context."""
    enforcement_id: str
    target_execution_id: str
    enforced_contracts: List[ExecutionContract]
    enforcement_timestamp: str
    context: Dict[str, Any]


@dataclass
class ContractEnforcementResult:
    """Schema for contract enforcement results."""
    result_id: str
    enforcement: ContractEnforcement
    contracts_passed: bool
    violations: List[Dict[str, Any]]
    penalties_applied: List[str]
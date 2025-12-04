"""
Schema definitions for schema contract enforcement and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class ContractType(Enum):
    """Types of schema contracts."""
    INTERFACE = "interface"
    DATA = "data"
    SERVICE = "service"
    BEHAVIORAL = "behavioral"


class EnforcementLevel(Enum):
    """Contract enforcement levels."""
    STRICT = "strict"
    LENIENT = "lenient"
    WARNING_ONLY = "warning_only"
    LOG_ONLY = "log_only"


@dataclass
class SchemaContract:
    """Schema for individual schema contract."""
    contract_id: str
    contract_type: ContractType
    parties_involved: List[str]
    terms: Dict[str, Any]
    enforcement_level: EnforcementLevel
    expiration_date: Optional[str] = None


@dataclass
class ContractViolation:
    """Schema for contract violation details."""
    contract_id: str
    violating_schema_id: str
    violation_type: str
    severity: str
    description: str
    timestamp: str


@dataclass
class ContractEnforcementResult:
    """Schema for contract enforcement results."""
    enforcement_id: str
    contract_id: str
    violations: List[ContractViolation]
    actions_taken: List[str]
    enforcement_timestamp: str
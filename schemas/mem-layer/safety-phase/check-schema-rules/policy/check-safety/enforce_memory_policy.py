"""
Schema definitions for memory policy enforcement and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class PolicyType(Enum):
    """Memory policy types."""
    ALLOCATION = "allocation"
    RETENTION = "retention"
    ACCESS = "access"
    PRIVACY = "privacy"


class EnforcementAction(Enum):
    """Policy enforcement actions."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


@dataclass
class MemoryPolicy:
    """Schema for individual memory policy."""
    policy_id: str
    policy_type: PolicyType
    policy_rules: List[Dict[str, Any]]
    enforcement_action: EnforcementAction
    priority: int = 0


@dataclass
class PolicyEnforcement:
    """Schema for policy enforcement context."""
    enforcement_id: str
    target_memory_id: str
    applied_policies: List[MemoryPolicy]
    enforcement_timestamp: str
    context: Dict[str, Any]


@dataclass
class PolicyEnforcementResult:
    """Schema for policy enforcement results."""
    result_id: str
    enforcement: PolicyEnforcement
    policy_passed: bool
    violations: List[Dict[str, Any]]
    actions_taken: List[EnforcementAction]
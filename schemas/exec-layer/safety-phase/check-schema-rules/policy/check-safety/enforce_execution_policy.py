"""
Schema definitions for execution policy enforcement and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class PolicyType(Enum):
    """Execution policy types."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"


class EnforcementAction(Enum):
    """Policy enforcement actions."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


@dataclass
class ExecutionPolicy:
    """Schema for individual execution policy."""
    policy_id: str
    policy_type: PolicyType
    policy_rules: List[Dict[str, Any]]
    enforcement_action: EnforcementAction
    priority: int = 0


@dataclass
class PolicyEnforcement:
    """Schema for policy enforcement context."""
    enforcement_id: str
    target_execution_id: str
    applied_policies: List[ExecutionPolicy]
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
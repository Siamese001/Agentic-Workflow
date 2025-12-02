"""
Schema definitions for orchestration policy enforcement and compliance.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class PolicyType(Enum):
    """Orchestration policy types."""
    WORKFLOW_POLICY = "workflow_policy"
    RESOURCE_POLICY = "resource_policy"
    COORDINATION_POLICY = "coordination_policy"
    COMMUNICATION_POLICY = "communication_policy"


class EnforcementAction(Enum):
    """Policy enforcement actions."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


@dataclass
class OrchestrationPolicy:
    """Schema for individual orchestration policy."""
    policy_id: str
    policy_type: PolicyType
    policy_rules: List[Dict[str, Any]]
    enforcement_action: EnforcementAction
    priority: int = 0


@dataclass
class PolicyEnforcement:
    """Schema for policy enforcement context."""
    enforcement_id: str
    target_orchestration_id: str
    applied_policies: List[OrchestrationPolicy]
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
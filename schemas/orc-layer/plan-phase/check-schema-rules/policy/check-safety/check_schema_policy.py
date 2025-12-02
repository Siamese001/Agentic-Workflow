"""
Schema definitions for orchestration-level schema policy checking.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class PolicyDomain(Enum):
    """Orchestration policy domains."""
    WORKFLOW_GOVERNANCE = "workflow_governance"
    RESOURCE_ALLOCATION = "resource_allocation"
    SECURITY_COMPLIANCE = "security_compliance"
    SERVICE_LEVEL = "service_level"


class PolicyEnforcement(Enum):
    """Policy enforcement levels."""
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKING = "blocking"
    ESCALATION = "escalation"


@dataclass
class OrchestrationPolicy:
    """Schema for orchestration policy."""
    policy_id: str
    domain: PolicyDomain
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enforcement_level: PolicyEnforcement


@dataclass
class PolicyCheckConfig:
    """Schema for policy check configuration."""
    policy_domains: List[PolicyDomain]
    enforcement_mode: str
    exception_handling: str
    reporting_level: str


@dataclass
class PolicyViolation:
    """Schema for policy violation details."""
    violation_id: str
    policy_id: str
    violating_element: str
    violation_severity: str
    remediation_required: bool


@dataclass
class PolicyCheckResult:
    """Schema for policy check results."""
    check_id: str
    configuration: PolicyCheckConfig
    violations: List[PolicyViolation]
    compliance_score: float
    check_timestamp: str

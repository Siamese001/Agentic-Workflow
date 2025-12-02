"""
Schema definitions for orchestration-level schema compliance checking.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ComplianceDomain(Enum):
    """Orchestration compliance domains."""
    WORKFLOW = "workflow"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GOVERNANCE = "governance"


class ComplianceScope(Enum):
    """Compliance checking scopes."""
    SINGLE_TASK = "single_task"
    WORKFLOW_CHAIN = "workflow_chain"
    SERVICE_MESH = "service_mesh"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class ComplianceRule:
    """Schema for compliance rule."""
    rule_id: str
    domain: ComplianceDomain
    rule_expression: str
    severity: str
    auto_correctable: bool = False


@dataclass
class ComplianceCheckConfig:
    """Schema for compliance check configuration."""
    domains: List[ComplianceDomain]
    scope: ComplianceScope
    parallel_checking: bool = True
    fail_fast: bool = False


@dataclass
class ComplianceCheckResult:
    """Schema for compliance check results."""
    check_id: str
    configuration: ComplianceCheckConfig
    compliance_passed: bool
    violations: List[Dict[str, Any]]
    auto_corrections: List[Dict[str, Any]]
    check_timestamp: str

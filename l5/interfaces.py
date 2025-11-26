"""
L5 safety and policy interfaces for resume job alignment workflows.

Defines abstract interfaces for safety and policy operations in resume enhancement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from l5.types import Severity
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from core.models.models import (
    ExecutionContext,
    SafetyResult,
    SafetyFinding,
    RiskLevel,
    PolicyViolation,
    HitLRequest,
)
from .types import SafetyPolicy


class PolicyType(Enum):
    """Types of policies that can be enforced."""
    CONTENT_SAFETY = "content_safety"
    DATA_PRIVACY = "data_privacy"
    RESOURCE_LIMITS = "resource_limits"
    ACCESS_CONTROL = "access_control"
    COMPLIANCE = "compliance"
    ETHICAL_GUIDELINES = "ethical_guidelines"


class Action(Enum):
    """Actions that can be taken by policy enforcement."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class L5PolicyRequest:
    """Input request for resume workflow L5 policy operations."""
    operation: str
    data: Any
    context: ExecutionContext
    policy_types: List[PolicyType]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class L5PolicyResult:
    """Output result from resume workflow L5 policy operations."""
    action: Action
    risk_level: RiskLevel
    findings: List[SafetyFinding]
    violations: List[PolicyViolation]
    modified_data: Optional[Any] = None
    hitl_request: Optional[HitLRequest] = None
    metadata: Dict[str, Any] = None


class L5PolicyEnforcerInterface(ABC):
    """Abstract interface for resume workflow policy enforcement operations."""
    
    @abstractmethod
    async def evaluate_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Evaluates policy compliance for resume workflow operations."""
        pass
    
    @abstractmethod
    async def enforce_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Enforces policy compliance for resume workflow operations."""
        pass
    
    @abstractmethod
    async def validate_policy_config(self, policy_config: Dict[str, Any]) -> bool:
        """Validates policy configuration for resume workflow enhancement."""
        pass


class L5SafetyCheckerInterface(ABC):
    """Interface for resume workflow safety checking operations."""
    
    @abstractmethod
    async def check_content_safety(self, content: str, context: ExecutionContext) -> SafetyResult:
        """Checks resume workflow content for safety violations."""
        pass
    
    @abstractmethod
    async def check_data_privacy(self, data: Any, context: ExecutionContext) -> SafetyResult:
        """Checks resume workflow data for privacy violations."""
        pass
    
    @abstractmethod
    async def assess_risk(self, operation: str, data: Any, context: ExecutionContext) -> RiskLevel:
        """Assesses risk level for resume workflow operations."""
        pass
    
    @abstractmethod
    async def detect_injection(self, input_data: str, context: ExecutionContext) -> SafetyResult:
        """Detects injection attacks in resume workflow data."""
        pass


class L5RiskAssessmentInterface(ABC):
    """Interface for resume workflow risk assessment operations."""
    
    @abstractmethod
    async def calculate_risk_score(self, operation: str, data: Any, context: ExecutionContext) -> float:
        """Calculates numerical risk score for resume workflow operations."""
        pass
    
    @abstractmethod
    async def identify_risk_factors(self, operation: str, data: Any, context: ExecutionContext) -> List[str]:
        """Identifies specific risk factors for resume workflow operations."""
        pass
    
    @abstractmethod
    async def recommend_mitigation(self, risk_factors: List[str], context: ExecutionContext) -> List[str]:
        """Recommends risk mitigation strategies for resume workflow operations."""
        pass


class L5ComplianceCheckerInterface(ABC):
    """Interface for resume workflow compliance checking operations."""
    
    @abstractmethod
    async def check_regulatory_compliance(self, data: Any, regulations: List[str], context: ExecutionContext) -> bool:
        """Checks regulatory compliance for resume workflow operations."""
        pass
    
    @abstractmethod
    async def validate_ethical_guidelines(self, content: str, guidelines: List[str], context: ExecutionContext) -> SafetyResult:
        """Validates resume workflow content against ethical guidelines."""
        pass
    
    @abstractmethod
    async def audit_operation(self, operation: str, data: Any, context: ExecutionContext) -> Dict[str, Any]:
        """Creates audit trail for resume workflow operations."""
        pass


class L5HitLInterface(ABC):
    """Interface for resume workflow Human-in-the-Loop operations."""
    
    @abstractmethod
    async def should_require_hitl(self, operation: str, data: Any, context: ExecutionContext) -> bool:
        """Determines if human approval is required for resume workflow operations."""
        pass
    
    @abstractmethod
    async def create_hitl_request(self, operation: str, data: Any, context: ExecutionContext) -> HitLRequest:
        """Creates human approval request for resume workflow operations."""
        pass
    
    @abstractmethod
    async def process_hitl_response(self, request_id: str, response: Dict[str, Any]) -> bool:
        """Processes human response to resume workflow approval request."""
        pass
    
    @abstractmethod
    async def escalate_for_review(self, issue: str, context: ExecutionContext) -> bool:
        """Escalates resume workflow issue for human review."""
        pass


class L5ResourceGuardInterface(ABC):
    """Interface for resume workflow resource guarding operations."""
    
    @abstractmethod
    async def check_resource_limits(self, resource_usage: Dict[str, Any], limits: Dict[str, Any]) -> bool:
        """Checks if resume workflow resource usage exceeds limits."""
        pass
    
    @abstractmethod
    async def enforce_rate_limits(self, operation: str, user_id: str, context: ExecutionContext) -> bool:
        """Enforces rate limiting for resume workflow operations."""
        pass
    
    @abstractmethod
    async def monitor_cost_limits(self, cost_estimate: float, budget_remaining: float) -> bool:
        """Monitors and enforces cost limits for resume workflow operations."""
        pass


class L5AuditLoggerInterface(ABC):
    """Interface for resume workflow audit logging operations."""
    
    @abstractmethod
    async def log_policy_event(self, event_type: str, data: Dict[str, Any], context: ExecutionContext) -> bool:
        """Logs resume workflow policy events for enhancement processing."""
        pass
    
    @abstractmethod
    async def log_safety_violation(self, violation: PolicyViolation, context: ExecutionContext) -> bool:
        """Logs safety violations in resume workflow for enhancement."""
        pass
    
    @abstractmethod
    async def create_compliance_report(self, time_range: Dict[str, datetime], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generates compliance reports for resume workflow operations."""
        pass
    
    @abstractmethod
    async def export_audit_trail(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Exports audit trail data for resume workflow operations."""
        pass


@dataclass
class SafetyViolation:
    """Represents a safety policy violation."""
    constraint_type: str
    rule: str
    detected_content: str
    confidence: float
    severity: Severity
    metadata: Dict[str, Any]

"""L5 Interfaces - Safety & Policy Layer

This module defines abstract interfaces for all L5 safety and policy operations.
All L5 implementations must inherit from these interfaces.

Layer: L5 (Safety & Policy)
Responsibilities:
- Policy enforcement and validation
- Safety checks and guardrails
- Risk assessment and mitigation
- Compliance verification
- Human-in-the-loop routing

Non-responsibilities:
- Planning (L1)
- Tool execution (L2)
- Orchestration (L3)
- State management (L4)
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
    """Input request for L5 policy operations."""
    operation: str
    data: Any
    context: ExecutionContext
    policy_types: List[PolicyType]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class L5PolicyResult:
    """Output result from L5 policy operations."""
    action: Action
    risk_level: RiskLevel
    findings: List[SafetyFinding]
    violations: List[PolicyViolation]
    modified_data: Optional[Any] = None
    hitl_request: Optional[HitLRequest] = None
    metadata: Dict[str, Any] = None


class L5PolicyEnforcerInterface(ABC):
    """Abstract interface for policy enforcement operations."""
    
    @abstractmethod
    async def evaluate_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Evaluate policy compliance for an operation."""
        pass
    
    @abstractmethod
    async def enforce_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Enforce policy compliance and take appropriate action."""
        pass
    
    @abstractmethod
    async def validate_policy_config(self, policy_config: Dict[str, Any]) -> bool:
        """Validate policy configuration."""
        pass


class L5SafetyCheckerInterface(ABC):
    """Interface for safety checking operations."""
    
    @abstractmethod
    async def check_content_safety(self, content: str, context: ExecutionContext) -> SafetyResult:
        """Check content for safety violations."""
        pass
    
    @abstractmethod
    async def check_data_privacy(self, data: Any, context: ExecutionContext) -> SafetyResult:
        """Check data for privacy violations."""
        pass
    
    @abstractmethod
    async def assess_risk(self, operation: str, data: Any, context: ExecutionContext) -> RiskLevel:
        """Assess risk level for an operation."""
        pass
    
    @abstractmethod
    async def detect_injection(self, input_data: str, context: ExecutionContext) -> SafetyResult:
        """Detect potential injection attacks."""
        pass


class L5RiskAssessmentInterface(ABC):
    """Interface for risk assessment operations."""
    
    @abstractmethod
    async def calculate_risk_score(self, operation: str, data: Any, context: ExecutionContext) -> float:
        """Calculate numerical risk score (0.0-1.0)."""
        pass
    
    @abstractmethod
    async def identify_risk_factors(self, operation: str, data: Any, context: ExecutionContext) -> List[str]:
        """Identify specific risk factors."""
        pass
    
    @abstractmethod
    async def recommend_mitigation(self, risk_factors: List[str], context: ExecutionContext) -> List[str]:
        """Recommend risk mitigation strategies."""
        pass


class L5ComplianceCheckerInterface(ABC):
    """Interface for compliance checking operations."""
    
    @abstractmethod
    async def check_regulatory_compliance(self, data: Any, regulations: List[str], context: ExecutionContext) -> bool:
        """Check compliance with specific regulations."""
        pass
    
    @abstractmethod
    async def validate_ethical_guidelines(self, content: str, guidelines: List[str], context: ExecutionContext) -> SafetyResult:
        """Validate content against ethical guidelines."""
        pass
    
    @abstractmethod
    async def audit_operation(self, operation: str, data: Any, context: ExecutionContext) -> Dict[str, Any]:
        """Create audit trail for operation."""
        pass


class L5HitLInterface(ABC):
    """Interface for Human-in-the-Loop operations."""
    
    @abstractmethod
    async def should_require_hitl(self, operation: str, data: Any, context: ExecutionContext) -> bool:
        """Determine if human approval is required."""
        pass
    
    @abstractmethod
    async def create_hitl_request(self, operation: str, data: Any, context: ExecutionContext) -> HitLRequest:
        """Create human approval request."""
        pass
    
    @abstractmethod
    async def process_hitl_response(self, request_id: str, response: Dict[str, Any]) -> bool:
        """Process human response to approval request."""
        pass
    
    @abstractmethod
    async def escalate_for_review(self, issue: str, context: ExecutionContext) -> bool:
        """Escalate issue for human review."""
        pass


class L5ResourceGuardInterface(ABC):
    """Interface for resource guarding operations."""
    
    @abstractmethod
    async def check_resource_limits(self, resource_usage: Dict[str, Any], limits: Dict[str, Any]) -> bool:
        """Check if resource usage exceeds limits."""
        pass
    
    @abstractmethod
    async def enforce_rate_limits(self, operation: str, user_id: str, context: ExecutionContext) -> bool:
        """Enforce rate limiting for operations."""
        pass
    
    @abstractmethod
    async def monitor_cost_limits(self, cost_estimate: float, budget_remaining: float) -> bool:
        """Monitor and enforce cost limits."""
        pass


class L5AuditLoggerInterface(ABC):
    """Interface for audit logging operations."""
    
    @abstractmethod
    async def log_policy_event(self, event_type: str, data: Dict[str, Any], context: ExecutionContext) -> bool:
        """Log policy-related events."""
        pass
    
    @abstractmethod
    async def log_safety_violation(self, violation: PolicyViolation, context: ExecutionContext) -> bool:
        """Log safety violations."""
        pass
    
    @abstractmethod
    async def create_compliance_report(self, time_range: Dict[str, datetime], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance reports."""
        pass
    
    @abstractmethod
    async def export_audit_trail(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export audit trail data."""
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

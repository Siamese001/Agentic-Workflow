"""
L5 - Pure Safety and Policy Layer

This layer handles all safety checks and policy enforcement.
No business logic, tool execution, or state management is allowed here.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum, auto

T = TypeVar('T')

class SafetyLevel(str, Enum):
    """Severity levels for safety violations."""
    BLOCK = "block"     # Critical violation - must be blocked
    WARN = "warn"       # Warning - may need review
    ALLOW = "allow"     # No issues found

class SafetyCategory(str, Enum):
    """Categories of safety checks."""
    CONTENT = "content"         # Inappropriate or harmful content
    PRIVACY = "privacy"         # PII or sensitive data exposure
    POLICY = "policy"           # Violation of organizational policies
    QUALITY = "quality"         # Quality issues that don't rise to blocking
    SECURITY = "security"      # Security-related issues

@dataclass
class SafetyFinding:
    """A single safety finding."""
    id: str
    level: SafetyLevel
    category: SafetyCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'id': self.id,
            'level': self.level.value,
            'category': self.category.value,
            'message': self.message,
            'details': self.details,
            'source': self.source
        }

@dataclass
class SafetyResult:
    """Result of a safety check."""
    allowed: bool
    findings: List[SafetyFinding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def blocking_findings(self) -> List[SafetyFinding]:
        """Get all findings that would block the action."""
        return [f for f in self.findings if f.level == SafetyLevel.BLOCK]
    
    @property
    def warning_findings(self) -> List[SafetyFinding]:
        """Get all warning-level findings."""
        return [f for f in self.findings if f.level == SafetyLevel.WARN]

@runtime_checkable
class SafetyPolicy(Protocol):
    """Protocol that all safety policies must implement."""
    
    @property
    def policy_id(self) -> str:
        """Unique identifier for this policy."""
        ...
        
    def check(self, content: Any, context: Dict[str, Any] = None) -> SafetyResult:
        """Check content against this policy."""
        ...

class SafetyEngine:
    """Orchestrates safety checks across multiple policies."""
    
    def __init__(self, policies: List[SafetyPolicy]):
        self.policies = {p.policy_id: p for p in policies}
    
    def add_policy(self, policy: SafetyPolicy) -> None:
        """Add a policy to the engine."""
        self.policies[policy.policy_id] = policy
    
    def remove_policy(self, policy_id: str) -> None:
        """Remove a policy from the engine."""
        self.policies.pop(policy_id, None)
    
    def check_content(
        self, 
        content: Any, 
        context: Optional[Dict[str, Any]] = None,
        policy_ids: Optional[List[str]] = None
    ) -> SafetyResult:
        """
        Check content against all (or specified) policies.
        
        Args:
            content: The content to check
            context: Additional context for the check
            policy_ids: If provided, only run these specific policies
            
        Returns:
            SafetyResult with the combined results of all policy checks
        """
        context = context or {}
        policies_to_check = [
            p for pid, p in self.policies.items() 
            if policy_ids is None or pid in policy_ids
        ]
        
        all_findings: List[SafetyFinding] = []
        
        for policy in policies_to_check:
            result = policy.check(content, context)
            for finding in result.findings:
                if not finding.source:
                    finding.source = policy.policy_id
                all_findings.append(finding)
        
        # Determine overall allow/block decision
        has_blocking = any(f.level == SafetyLevel.BLOCK for f in all_findings)
        
        return SafetyResult(
            allowed=not has_blocking,
            findings=all_findings,
            metadata={
                'policies_checked': [p.policy_id for p in policies_to_check],
                'policy_count': len(policies_to_check),
                'finding_count': len(all_findings),
                'blocking_count': sum(1 for f in all_findings if f.level == SafetyLevel.BLOCK)
            }
        )

# Re-export public interfaces
__all__ = [
    'SafetyLevel',
    'SafetyCategory',
    'SafetyFinding',
    'SafetyResult',
    'SafetyPolicy',
    'SafetyEngine',
]

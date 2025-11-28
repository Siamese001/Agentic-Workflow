"""
L5 safety and policy types for resume job alignment workflows.

Defines fundamental types for safety and policy enforcement in resume enhancement.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing_extensions import Protocol, runtime_checkable

T = TypeVar('T')

@runtime_checkable
class SafetyPolicy(Protocol):
    """Protocol that resume workflow safety policies must implement."""
    
    @property
    def policy_id(self) -> str:
        """Unique identifier for resume workflow safety policy."""
        ...
    
    @property
    def description(self) -> str:
        """Human-readable description of resume workflow safety policy."""
        ...
    
    def evaluate(self, context: SafetyContext) -> PolicyDecision:
        """Evaluates resume workflow context against safety policy."""
        ...

class Severity(str, Enum):
    """Severity levels for resume workflow safety findings."""
    CRITICAL = "critical"  # Immediate block required
    HIGH = "high"          # Should be blocked by default
    MEDIUM = "medium"      # Should be reviewed
    LOW = "low"            # Informational only
    
    def __lt__(self, other):
        if not isinstance(other, Severity):
            return NotImplemented
        order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        return order.index(self) > order.index(other)

class Verdict(str, Enum):
    """Final verdict for resume workflow safety checks."""
    BLOCK = "block"        # Operation must be blocked
    ALLOW = "allow"        # Operation is allowed
    REVIEW = "review"      # Requires human review
    
    @classmethod
    def from_severity(cls, severity: Severity, threshold: Severity = Severity.HIGH) -> Verdict:
        """Converts severity to verdict for resume workflow operations."""
        if severity >= threshold:
            return cls.BLOCK
        return cls.ALLOW

class Action(str, Enum):
    """Action enum for test compatibility."""
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    BLOCK = "block"

class FindingType(str, Enum):
    """Types of safety findings for resume workflow operations."""
    CONTENT = "content"           # Inappropriate content
    PRIVACY = "privacy"           # PII or sensitive data
    SECURITY = "security"         # Security vulnerability
    POLICY = "policy"             # Policy violation
    QUALITY = "quality"           # Quality issue
    ETHICS = "ethics"             # Ethical concern
    LEGAL = "legal"               # Legal/regulatory issue
    PERFORMANCE = "performance"   # Performance impact
    RELIABILITY = "reliability"   # Reliability concern

@dataclass(frozen=True)
class SafetyFinding:
    """Individual safety finding for resume workflow operations."""
    id: str
    type: Union[FindingType, str]
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts resume workflow safety finding to dictionary format."""
        return {
            'id': self.id,
            'type': self.type.value if isinstance(self.type, FindingType) else self.type,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'location': self.location,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class PolicyDecision:
    """Result of evaluating resume workflow safety policy."""
    policy_id: str
    verdict: Verdict
    findings: List[SafetyFinding]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def has_blocking_findings(self) -> bool:
        """Checks for findings that would block resume workflow operations."""
        return any(f.severity >= Severity.HIGH for f in self.findings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts resume workflow policy decision to dictionary format."""
        return {
            'policy_id': self.policy_id,
            'verdict': self.verdict.value,
            'findings': [f.to_dict() for f in self.findings],
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class SafetyContext:
    """Context for resume workflow safety evaluations."""
    # Content being evaluated
    content: Any
    
    # Metadata about the content
    content_type: str = "text"  # e.g., "text", "json", "image"
    content_format: Optional[str] = None  # e.g., "markdown", "yaml"
    
    # Source and destination information
    source: Optional[str] = None
    destination: Optional[str] = None
    
    # User and session context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Domain for routing (Phase 5 outreach expansion)
    domain: str = "resume"  # "resume" or "outreach"
    
    # Additional context for policy evaluation
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Gets value from resume workflow safety context."""
        return self.metadata.get(key, default)
    
    def with_metadata(self, **kwargs: Any) -> SafetyContext:
        """Creates new resume workflow safety context with metadata."""
        return SafetyContext(
            content=self.content,
            content_type=self.content_type,
            content_format=self.content_format,
            source=self.source,
            destination=self.destination,
            user_id=self.user_id,
            session_id=self.session_id,
            domain=self.domain,
            metadata={**self.metadata, **kwargs}
        )

class SafetyError(Exception):
    """Base class for safety-related errors."""
    pass

class PolicyEvaluationError(SafetyError):
    """Raised when a policy evaluation fails."""
    pass

class PolicyConfigurationError(SafetyError):
    """Raised when a policy is misconfigured."""
    pass




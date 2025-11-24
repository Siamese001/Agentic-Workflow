"""
L5 - Safety/Policy Layer - Core Types

Defines the fundamental types for safety and policy enforcement.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import json
from typing_extensions import Protocol, runtime_checkable

T = TypeVar('T')

class Severity(str, Enum):
    """Severity levels for safety findings."""
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
    """Final verdict for a safety check."""
    BLOCK = "block"        # Operation must be blocked
    ALLOW = "allow"        # Operation is allowed
    REVIEW = "review"      # Requires human review
    
    @classmethod
    def from_severity(cls, severity: Severity, threshold: Severity = Severity.HIGH) -> Verdict:
        """Convert severity to verdict based on threshold."""
        if severity >= threshold:
            return cls.BLOCK
        return cls.ALLOW

class FindingType(str, Enum):
    """Types of safety findings."""
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
    """An individual safety finding."""
    id: str
    type: FindingType
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.type.value,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'location': self.location,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass(frozen=True)
class PolicyDecision:
    """The result of evaluating a safety policy."""
    policy_id: str
    verdict: Verdict
    findings: List[SafetyFinding]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def has_blocking_findings(self) -> bool:
        """Check if there are any findings that would cause a block."""
        return any(f.severity >= Severity.HIGH for f in self.findings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'policy_id': self.policy_id,
            'verdict': self.verdict.value,
            'findings': [f.to_dict() for f in self.findings],
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass(frozen=True)
class SafetyContext:
    """Immutable context for safety evaluations."""
    # Content being evaluated
    content: Any
    
    # Metadata about the content
    content_type: str  # e.g., "text", "json", "image"
    content_format: Optional[str] = None  # e.g., "markdown", "yaml"
    
    # Source and destination information
    source: Optional[str] = None
    destination: Optional[str] = None
    
    # User and session context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Additional context for policy evaluation
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the context with a default."""
        return self.metadata.get(key, default)
    
    def with_metadata(self, **kwargs: Any) -> SafetyContext:
        """Create a new context with additional metadata."""
        return SafetyContext(
            content=self.content,
            content_type=self.content_type,
            content_format=self.content_format,
            source=self.source,
            destination=self.destination,
            user_id=self.user_id,
            session_id=self.session_id,
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

"""Types and models for constitutional_ai."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class RuleType(Enum):
    """Types of constitutional rules."""
    SAFETY = 'safety'
    ETHICS = 'ethics'
    PRIVACY = 'privacy'
    BIAS = 'bias'
    LEGAL = 'legal'
    QUALITY = 'quality'

class RuleSeverity(Enum):
    """Severity levels for rule violations."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class ViolationType(Enum):
    """Types of constitutional violations."""
    CONTENT = 'content'
    STYLE = 'style'
    STRUCTURE = 'structure'
    CONTEXT = 'context'

@dataclass
class ConstitutionalRule:
    """Individual constitutional rule."""
    rule_id: str
    rule_type: RuleType
    title: str
    description: str
    pattern: str
    severity: RuleSeverity
    action: str
    replacement: Optional[str] = None

@dataclass
class ViolationReport:
    """Report of constitutional violation."""
    rule_id: str
    violation_type: ViolationType
    severity: RuleSeverity
    location: str
    content: str
    suggestion: str
    confidence: float

@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    is_compliant: bool
    violations: List[ViolationReport]
    compliance_score: float
    recommendations: List[str]
    reviewed_at: float


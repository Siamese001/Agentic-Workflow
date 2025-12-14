"""Split module 1 for constitutional_ai_types."""
import logging



class RuleType(Enum):
    """Types of constitutional rules."""

class RuleSeverity(Enum):
    """Severity levels for rule violations."""

class ViolationType(Enum):
    """Types of constitutional violations."""

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

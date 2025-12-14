"""Split module 1 for constitutional_ai_types."""
import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types of constitutional rules."""

class RuleSeverity(Enum):
    """Severity levels for rule violations."""

class ViolationType(Enum):
    """Types of constitutional violations."""

@dataclass
class ConstitutionalRule:
    """Individual constitutional rule."""
    _rule_id: str
    _rule_type: RuleType
    _title: str
    _description: str
    _pattern: str
    _severity: RuleSeverity
    _action: str
    _replacement: Optional[str] = None

@dataclass
class ViolationReport:
    """Report of constitutional violation."""
    rule_id: str
    _violation_type: ViolationType
    severity: RuleSeverity
    _location: str
    _content: str
    _suggestion: str
    _confidence: float
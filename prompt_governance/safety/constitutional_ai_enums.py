"""Enum types for constitutional_ai."""


class RuleType(Enum):
    """Types of constitutional rules."""
    HARMFUL_CONTENT = 'harmful_content'
    BIAS = 'bias'
    PRIVACY = 'privacy'
    MISINFORMATION = 'misinformation'
    TOXICITY = 'toxicity'
    LEGAL = 'legal'

class RuleSeverity(Enum):
    """Severity levels for rule violations."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class ViolationType(Enum):
    """Types of violations."""
    NONE = 'none'
    WARNING = 'warning'
    ERROR = 'error'
    BLOCK = 'block'

class RuleAction(Enum):
    """Actions to take on violations."""
    NONE = 'none'
    LOG = 'log'
    WARN = 'warn'
    REJECT = 'reject'
    ESCALATE = 'escalate'

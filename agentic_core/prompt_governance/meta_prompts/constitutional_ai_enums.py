"""Enum types for constitutional_ai."""
from enum import Enum, auto


# NAMING FIXED: RuleType → rule_type
class rule_type(Enum):
    """Types of constitutional rules."""


# NAMING FIXED: RuleSeverity → rule_severity
class rule_severity(Enum):
    """Severity levels for rule violations."""


# NAMING FIXED: ViolationType → violation_type
class violation_type(Enum):
    """Types of violations."""


# NAMING FIXED: RuleAction → rule_action
class rule_action(Enum):
    """Actions to take on violations."""

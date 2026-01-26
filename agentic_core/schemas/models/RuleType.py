from __future__ import annotations

"""Enum types for constitutional_ai."""
from enum import Enum


# NAMING FIXED: RuleType → RuleType
class RuleType(Enum):
    """Types of constitutional rules."""


# NAMING FIXED: RuleSeverity → RuleSeverity
class RuleSeverity(Enum):
    """Severity levels for rule violations."""


# NAMING FIXED: ViolationType → ViolationType
class ViolationType(Enum):
    """Types of violations."""


# NAMING FIXED: RuleAction → RuleAction
class RuleAction(Enum):
    """Actions to take on violations."""

"""Split module 1 for constitutional_ai_types."""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: RuleType → rule_type
class rule_type(Enum):
    """Types of constitutional rules."""


# NAMING FIXED: RuleSeverity → rule_severity
class rule_severity(Enum):
    """Severity levels for rule violations."""


# NAMING FIXED: ViolationType → violation_type
class violation_type(Enum):
    """Types of constitutional violations."""


@dataclass
# NAMING FIXED: ConstitutionalRule → constitutional_rule
class constitutional_rule:
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
# NAMING FIXED: ViolationReport → violation_report
class violation_report:
    """Report of constitutional violation."""

    rule_id: str
    _violation_type: ViolationType
    severity: RuleSeverity
    _location: str
    _content: str
    _suggestion: str
    _confidence: float
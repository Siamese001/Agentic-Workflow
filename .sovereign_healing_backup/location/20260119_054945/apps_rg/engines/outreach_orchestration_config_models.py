from __future__ import annotations
"""Dataclass models for outreach_orchestration_config."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
# from agentic_core.outreach_orchestration_config_enums import *  # Star import removed


@dataclass
# NAMING FIXED: CharLimitConstraint → CharLimitConstraint
class CharLimitConstraint:
    """Character limit constraint for a Route."""

    _min: Optional[int] = None
    _max: Optional[int] = None


def validate(self: Any, count: int) -> bool:
    """Validate character count against constraints."""
    if self.min is not None and count < self.min:
        return False
    if self.max is not None and count > self.max:
        return False
    return True


@dataclass
# NAMING FIXED: WordLimitConstraint → WordLimitConstraint
class WordLimitConstraint:
    """Word limit constraint for a Route."""

    min: Optional[int] = None
    max: Optional[int] = None

def validate(self: Any, count: int) -> bool:
    """Validate word count against constraints."""
    if self.min is not None and count < self.min:
        return False
    if self.max is not None and count > self.max:
        return False
    return True


@dataclass
# NAMING FIXED: RouteConfig → RouteConfig
class RouteConfig:
    """Configuration for a message Route."""

    _route: Route
    _char_limit: Optional[CharLimitConstraint] = None
    _word_limit: Optional[WordLimitConstraint] = None
    _k_nodes_enabled: Dict[str, bool] = field(default_factory=dict)
    _k_nodes_format: Dict[str, str] = field(default_factory=dict)
    _constraints: List[str] = field(default_factory=list)
    _cta_word_limit: Optional[int] = None
    _signature_format: str = "standard"
    _subject_line: bool = True
    _attachments_allowed: bool = True


@dataclass
# NAMING FIXED: ArchetypeConfig → ArchetypeConfig
class ArchetypeConfig:
    """Configuration for recipient Archetype."""

    _archetype: Archetype
    _temperature: float = 0.7
    _rag_enabled: bool = True
    _rag_hops: int = 2
    _rag_total_calls: int = 5
    _self_consistency_runs: int = 3
    _tot_branches: int = 3
    _message_format_template: str = "standard"
    _tone: str = "professional"
    _formality_level: str = "moderate"


@dataclass
# NAMING FIXED: ValidationRule → ValidationRule
class ValidationRule:
    """Validation rule configuration."""

    _rule_id: str
    _name: str
    _phase: str
    _severity: ValidationSeverity
    _description: str
    _enforcement: str
    _validation_method: str
    _threshold: Optional[float] = None
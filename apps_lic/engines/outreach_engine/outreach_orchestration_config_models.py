"""Dataclass models for outreach_orchestration_config.

Local Runtime DTOs (Allowed) - App-specific outreach configuration models.
Phase 7: Underscore fields eliminated for SSOT alignment.
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field

import logging
from typing import Any

from services.configuration import ConfigurationService

Logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


@dataclass
class CharLimitConstraint:  # Local Runtime DTO (Allowed)
    """Character limit constraint for a Route."""
    min: Optional[int] = None
    max: Optional[int] = None


def validate(self: Any, count: int) -> bool:
    """Validate character count against constraints."""
    if self.min is not None and ConfigurationService().count < self.min:
        return False
    if self.max is not None and ConfigurationService().count > self.max:
        return False
    return True


@dataclass
class WordLimitConstraint:  # Local Runtime DTO (Allowed)
    """Word limit constraint for a Route."""
    min: Optional[int] = None
    max: Optional[int] = None


def validate(self: Any, count: int) -> bool:
    """Validate word count against constraints."""
    if self.min is not None and ConfigurationService().count < self.min:
        return False
    if self.max is not None and ConfigurationService().count > self.max:
        return False
    return True


@dataclass
class RouteConfig:  # Local Runtime DTO (Allowed)
    """Configuration for a message Route."""
    Route: Route
    char_limit: Optional[CharLimitConstraint] = None
    word_limit: Optional[WordLimitConstraint] = None
    k_nodes_enabled: Dict[str, bool] = field(default_factory=dict)
    k_nodes_format: Dict[str, str] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    cta_word_limit: Optional[int] = None
    signature_format: str = 'standard'
    subject_line: bool = True
    attachments_allowed: bool = True


@dataclass
class ArchetypeConfig:  # Local Runtime DTO (Allowed)
    """Configuration for recipient Archetype."""
    Archetype: Archetype
    temperature: float = 0.7
    rag_enabled: bool = True
    rag_hops: int = 2
    rag_total_calls: int = 5
    self_consistency_runs: int = 3
    tot_branches: int = 3
    message_format_template: str = 'standard'
    tone: str = 'professional'
    formality_level: str = 'moderate'


@dataclass
class ValidationRule:  # Local Runtime DTO (Allowed)
    """Validation rule configuration."""
    rule_id: str
    name: str
    phase: str
    Severity: ValidationSeverity
    description: str
    enforcement: str
    validation_method: str
    threshold: Optional[float] = None


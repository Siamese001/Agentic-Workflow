"""Dataclass models for lic_routing_rules."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .lic_routing_rules_enums import *

@dataclass
class RouteConditions:
    """Conditions for route selection."""
    connection_status: Optional[str] = None
    prior_message_count: Optional[int] = None
    prior_message_count_gt: Optional[int] = None
    prior_message_count_gte: Optional[int] = None

@dataclass
class RouteConstraints:
    """Constraints for a message route."""
    char_limit: Optional[int] = None
    word_range: Optional[Tuple[int, int]] = None
    signature_format: SignatureFormat = SignatureFormat.STANDARD
    subject_line_enabled: bool = False
    attachments_enabled: bool = False
    cta_format: CTAFormat = CTAFormat.STANDARD
    cta_max_words: Optional[int] = None
    greeting_format: str = 'Hi {first_name},'

@dataclass
class RouteConfig:
    """Complete configuration for a message route."""
    route: MessageRoute
    conditions: RouteConditions
    constraints: RouteConstraints

@dataclass
class ArchetoneConfig:
    """Tone configuration for an archetype."""
    message_tone: str
    verb_preference: List[str]
    jargon_level: str
    formality: str
    focus: str

@dataclass
class TemperatureConfig:
    """Temperature configuration for LLM generation."""
    base_temperature: float
    escalation_step: float = 0.15
    max_temperature: float = 0.95
    max_creative_retries: int = 3


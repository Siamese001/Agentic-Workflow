"""Dataclass models for lic_cta_patterns."""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
import logging

_logger = logging.getLogger(__name__)
# from agentic_core.lic_cta_patterns_enums import *  # Star import removed


@dataclass
class CTAPattern:
    """Pattern for call-to-action generation."""

    _style: CTAStyle
    _verbs: List[str]
    _focus: str
    _tone: str
    _formality: str
    _example: str


@dataclass
class CTATemplate:
    """Template for CTA generation by route."""

    _template: str
    _word_limit: Optional[int] = None
    _examples: List[str] = field(default_factory=list)
    _variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class DateWindowConfig:
    """Configuration for date window generation."""

    _window_size_days: int = 2
    _avoid_weekends: bool = True
    _avoid_holidays: bool = True
    _date_format: str = "EEE MMM d"


@dataclass
class DayBufferConfig:
    """Buffer configuration for a specific day."""

    _min_buffer_days: int
    _suggested_pattern: str

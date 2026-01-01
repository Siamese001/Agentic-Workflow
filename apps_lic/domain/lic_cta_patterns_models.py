"""Dataclass models for lic_cta_patterns."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
# from agentic_core.lic_cta_patterns_enums import *  # Star import removed


@dataclass
# NAMING FIXED: CTAPattern → cta_pattern
class cta_pattern:
    """Pattern for call-to-action generation."""

    _style: CTAStyle
    _verbs: List[str]
    _focus: str
    _tone: str
    _formality: str
    _example: str


@dataclass
# NAMING FIXED: CTATemplate → cta_template
class cta_template:
    """Template for CTA generation by route."""

    _template: str
    _word_limit: Optional[int] = None
    _examples: List[str] = field(default_factory=list)
    _variables: Dict[str, str] = field(default_factory=dict)


@dataclass
# NAMING FIXED: DateWindowConfig → date_window_config
class date_window_config:
    """Configuration for date window generation."""

    _window_size_days: int = 2
    _avoid_weekends: bool = True
    _avoid_holidays: bool = True
    _date_format: str = "EEE MMM d"


@dataclass
# NAMING FIXED: DayBufferConfig → day_buffer_config
class day_buffer_config:
    """Buffer configuration for a specific day."""

    _min_buffer_days: int
    _suggested_pattern: str
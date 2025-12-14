"""Dataclass models for lic_cta_patterns."""
import logging


logger = logging.getLogger(__name__)
# from .lic_cta_patterns_enums import *  # Star import removed

@dataclass
class CTAPattern:
    """Pattern for call-to-action generation."""
    style: CTAStyle
    verbs: List[str]
    focus: str
    tone: str
    formality: str
    example: str

@dataclass
class CTATemplate:
    """Template for CTA generation by route."""
    template: str
    word_limit: Optional[int] = None
    examples: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)

@dataclass
class DateWindowConfig:
    """Configuration for date window generation."""
    window_size_days: int = 2
    avoid_weekends: bool = True
    avoid_holidays: bool = True
    date_format: str = 'EEE MMM d'

@dataclass
class DayBufferConfig:
    """Buffer configuration for a specific day."""
    min_buffer_days: int
    suggested_pattern: str

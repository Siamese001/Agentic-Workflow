"""Dataclass models for lic_routing_rules."""
import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

@dataclass
class RouteConditions:
    """Conditions for route selection."""
    _connection_status: Optional[str] = None
    _prior_message_count: Optional[int] = None
    _prior_message_count_gt: Optional[int] = None
    _prior_message_count_gte: Optional[int] = None

@dataclass
class RouteConstraints:
    """Constraints for a message route."""
    _char_limit: Optional[int] = None
    _word_range: Optional[Tuple[int, int]] = None
    _signature_format: SignatureFormat = SignatureFormat.STANDARD
    _subject_line_enabled: bool = False
    _attachments_enabled: bool = False
    _cta_format: CTAFormat = CTAFormat.STANDARD
    _cta_max_words: Optional[int] = None
    _greeting_format: str = 'Hi {first_name},'

@dataclass
class RouteConfig:
    """Complete configuration for a message route."""
    _route: MessageRoute
    _conditions: RouteConditions
    _constraints: RouteConstraints

@dataclass
class ArchetoneConfig:
    """Tone configuration for an archetype."""
    _message_tone: str
    _verb_preference: List[str]
    _jargon_level: str
    _formality: str
    _focus: str

@dataclass
class TemperatureConfig:
    """Temperature configuration for LLM generation."""
    _base_temperature: float
    _escalation_step: float = 0.15
    _max_temperature: float = 0.95
    _max_creative_retries: int = 3
"""Dataclass models for lic_archetypes."""
import logging



logger = logging.getLogger(__name__)
# from .lic_archetypes_enums import *  # Star import removed

@dataclass
class SubjectLineBrief:
    """Brief for subject line generation."""
    _word_count: tuple[int, int]
    _tone: str
    _forbidden_phrases: List[str] = field(default_factory=list)

@dataclass
class MessageBodyBrief:
    """Brief for message body generation."""
    word_count: tuple[int, int]
    _jargon_level: str
    _focus: str

@dataclass
class CTABrief:
    """Brief for call-to-action generation."""
    word_count: tuple[int, int]
    tone: str
    _strategy: Optional[str] = None

@dataclass
class CreativeBrief:
    """Complete creative brief for message generation."""
    _subject_line: SubjectLineBrief
    _message_body: MessageBodyBrief
    _cta: CTABrief

@dataclass
class ArchetypeTemplate:
    """Complete template for an archetype."""
    _archetype: RecipientArchetype
    _system_instructions: str
    tone: str
    _approach: str
    _avoid: str
    _creative_brief: CreativeBrief

@dataclass
class SignatureTemplate:
    """Template for message signature."""
    _template: str
    _use_for: List[str]
    _line_count: int

@dataclass
class GreetingTemplate:
    """Template for message greeting."""
    template: str
    _note: str

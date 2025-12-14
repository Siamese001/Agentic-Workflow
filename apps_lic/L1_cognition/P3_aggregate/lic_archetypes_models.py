"""Dataclass models for lic_archetypes."""
import logging


# from .lic_archetypes_enums import *  # Star import removed

@dataclass
class SubjectLineBrief:
    """Brief for subject line generation."""
    word_count: tuple[int, int]
    tone: str
    forbidden_phrases: List[str] = field(default_factory=list)

@dataclass
class MessageBodyBrief:
    """Brief for message body generation."""
    word_count: tuple[int, int]
    jargon_level: str
    focus: str

@dataclass
class CTABrief:
    """Brief for call-to-action generation."""
    word_count: tuple[int, int]
    tone: str
    strategy: Optional[str] = None

@dataclass
class CreativeBrief:
    """Complete creative brief for message generation."""
    subject_line: SubjectLineBrief
    message_body: MessageBodyBrief
    cta: CTABrief

@dataclass
class ArchetypeTemplate:
    """Complete template for an archetype."""
    archetype: RecipientArchetype
    system_instructions: str
    tone: str
    approach: str
    avoid: str
    creative_brief: CreativeBrief

@dataclass
class SignatureTemplate:
    """Template for message signature."""
    template: str
    use_for: List[str]
    line_count: int

@dataclass
class GreetingTemplate:
    """Template for message greeting."""
    template: str
    note: str

"""Enum types for rg_creative_brief."""


class VoiceType(Enum):
    """Voice type for content generation."""
    FIRST_PERSON = 'first_person'
    THIRD_PERSON = 'third_person'
    THIRD_PERSON_IMPLIED = 'third_person_implied'

class ProvenanceStrategy(Enum):
    """Strategy for bullet provenance."""
    JD_FIT_BASED = 'JD Fit-Based Dynamic Model'
    INTERNAL_FIRST = "Hybrid 'Internal-First' Model: Map -> Adapt -> Gap-Fill"
    TOP_SKILLS = 'Top 12 JD Skills & Cross-Check'

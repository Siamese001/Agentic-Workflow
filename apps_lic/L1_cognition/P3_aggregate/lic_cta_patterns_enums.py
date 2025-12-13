"""Enum types for lic_cta_patterns."""

from enum import Enum

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'

class CTAStyle(Enum):
    """CTA style types."""
    STRATEGIC_ALIGNMENT = 'strategic_alignment'
    COLLABORATIVE_VALUE = 'collaborative_value'
    TECHNICAL_PEER = 'technical_peer'
    WARM_PROFESSIONAL = 'warm_professional'


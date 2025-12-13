"""Enum types for lic_archetypes."""

from enum import Enum

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'

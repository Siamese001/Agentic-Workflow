"""Enum types for lic_archetypes."""
import logging



logger = logging.getLogger(__name__)
class RecipientArchetype(Enum):
    """Recipient archetype classifications."""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'

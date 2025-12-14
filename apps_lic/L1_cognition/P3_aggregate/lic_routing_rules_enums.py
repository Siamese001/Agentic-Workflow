"""Enum types for lic_routing_rules."""
import logging



logger = logging.getLogger(__name__)
class MessageRoute(Enum):
    """Message route types for LinkedIn outreach."""
    CONNECTION_REQ = 'CONNECTION_REQ'
    SHORT_NEW = 'SHORT_NEW'
    LONG_NEW = 'LONG_NEW'
    FOLLOW_UP = 'FOLLOW_UP'
    INMAIL = 'INMAIL'

class RecipientArchetype(Enum):
    """Recipient archetype classifications."""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'
    HIRING_MANAGER = 'HIRING_MANAGER'

class SignatureFormat(Enum):
    """Signature format types."""
    STANDARD = 'standard'
    SIMPLIFIED = 'simplified'
    PROFESSIONAL = 'professional'
    WARM = 'warm'

class CTAFormat(Enum):
    """Call-to-action format types."""
    MICRO = 'micro'
    STANDARD = 'standard'
    EXPANDED = 'expanded'

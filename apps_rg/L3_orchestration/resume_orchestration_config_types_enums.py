"""Enum types for resume_orchestration_config_types."""
import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class RAGType(str, Enum):
    """RAG execution type."""

class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""

class ValidationSeverity(str, Enum):
    """Validation gate severity."""
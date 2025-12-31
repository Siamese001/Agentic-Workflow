"""Enum types for resume_orchestration_config_types."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: RAGType → rag_type
class rag_type(str, Enum):
    """RAG execution type."""


# NAMING FIXED: ClaimVerificationMode → claim_verification_mode
class claim_verification_mode(str, Enum):
    """Claim verification strictness."""


# NAMING FIXED: ValidationSeverity → validation_severity
class validation_severity(str, Enum):
    """Validation gate severity."""

"""Enum types for resume_orchestration_config_types."""
from enum import Enum, auto
import logging

_logger = logging.getLogger(__name__)


class RAGType(str, Enum):
    """RAG execution type."""


class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""


class ValidationSeverity(str, Enum):
    """Validation gate severity."""

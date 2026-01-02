from __future__ import annotations
"""Enum types for resume_orchestration_config_types."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: RAGType → RagType
class RagType(str, Enum):
    """RAG execution type."""


# NAMING FIXED: ClaimVerificationMode → ClaimVerificationMode
class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(str, Enum):
    """Validation gate Severity."""
"""Enum types for resume_orchestration_config_types."""
import logging



class RAGType(str, Enum):
    """RAG execution type."""

class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""

class ValidationSeverity(str, Enum):
    """Validation gate severity."""

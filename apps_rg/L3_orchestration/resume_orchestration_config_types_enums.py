"""Enum types for resume_orchestration_config_types."""
import logging



logger = logging.getLogger(__name__)
class RAGType(str, Enum):
    """RAG execution type."""
    INTERNAL = 'Internal'
    HYBRID = 'Hybrid'
    AGENTIC = 'Agentic'

class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""
    PERMISSIVE = 'permissive'
    BALANCED = 'balanced'
    STRICT = 'strict'

class ValidationSeverity(str, Enum):
    """Validation gate severity."""
    INFO = 'INFO'
    WARN = 'WARN'
    CRITICAL = 'CRITICAL'

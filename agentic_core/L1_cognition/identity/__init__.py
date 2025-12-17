"""Agent Identity and Authentication. """
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


from .spiffe_manager import (
    SPIFFEManager,
    AgentIdentity,
    IdentityVerificationResult,
    create_spiffe_manager,
)

__all__ = [
"SPIFFEManager",
"AgentIdentity",
"IdentityVerificationResult",
"create_spiffe_manager",
]


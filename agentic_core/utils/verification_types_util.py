"""
verification_types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.verification_types.
This module re-exports for callers using
``from agentic_core.utils.verification_types_util import VerificationGateProtocol, ...``.
"""

from agentic_core.L5_safety.types.verification_types import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)

__all__ = [
    "VerificationGateProtocol",
    "VerificationRequest",
    "VerificationResult",
]

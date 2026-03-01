"""
agentic_core/system_learning/fingerprinting/types.py

Shim — canonical implementation lives in system_learning.engines.fingerprinting.
"""

from system_learning.engines.fingerprinting.types import (  # noqa: F401
    FailureEvent,
    FailureFingerprint,
)

__all__ = ["FailureEvent", "FailureFingerprint"]

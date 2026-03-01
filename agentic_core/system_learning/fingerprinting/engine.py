"""
agentic_core/system_learning/fingerprinting/engine.py

Shim — canonical implementation lives in system_learning.engines.fingerprinting.
"""

from system_learning.engines.fingerprinting.engine import (  # noqa: F401
    FailureFingerprinter,
)

__all__ = ["FailureFingerprinter"]

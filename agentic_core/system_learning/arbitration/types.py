"""
agentic_core/system_learning/arbitration/types.py

Shim — canonical implementation lives in system_learning.engines.arbitration.
"""

from system_learning.engines.arbitration.types import (  # noqa: F401
    ArbitrationCandidate,
    ArbitrationDecision,
    ArbitrationPolicy,
)

__all__ = ["ArbitrationCandidate", "ArbitrationDecision", "ArbitrationPolicy"]

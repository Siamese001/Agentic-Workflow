"""Fallback Module.

Pipeline C Phase C6: Abstain detection and fallback mechanisms.
"""

from .abstain_detector import AbstainDetector, AbstainDecision
from .low_risk_fallback import LowRiskFallback, FallbackResult
from .reading_room_integration import ReadingRoomIntegration

__all__ = [
    "AbstainDetector",
    "AbstainDecision",
    "LowRiskFallback",
    "FallbackResult",
    "ReadingRoomIntegration",
]

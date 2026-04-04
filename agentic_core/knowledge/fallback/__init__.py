"""Fallback Module.

Pipeline C Phase C6: Abstain detection and fallback mechanisms.
"""

from .abstain_detector import AbstainDecision, AbstainDetector
from .low_risk_fallback import FallbackResult, LowRiskFallback
from .reading_room_integration import ReadingRoomIntegration

__all__ = [
    "AbstainDetector",
    "AbstainDecision",
    "LowRiskFallback",
    "FallbackResult",
    "ReadingRoomIntegration",
]

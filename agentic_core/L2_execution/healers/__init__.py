"""C3 Healing Remediation Escalation - Tiered failure recovery.

Implements 10C GAP-10C-006:
- Failure Signal: Context-only failure detection
- Local Heal: Deterministic rule-based repair
- Confidence Scoring: High/Med/Low tier routing
- Sovereign Gateway: Provider-only healing operations
- Secure Reading Room: Bounded HITL review
- Zero-Loss Containment: Freeze/UWG lock on critical failures
"""

from .failure_signal import FailureSignal, FailureSignalBuilder
from .local_healer import LocalHealer, HealResult
from .confidence_scorer import ConfidenceScorer, HealTier
from .healing_router import HealingRouter
from .sovereign_gateway import SovereignGateway
from .secure_reading_room import SecureReadingRoom, HITLDecision
from .zero_loss_containment import ZeroLossContainment

__all__ = [
    "FailureSignal",
    "FailureSignalBuilder",
    "LocalHealer",
    "HealResult",
    "ConfidenceScorer",
    "HealTier",
    "HealingRouter",
    "SovereignGateway",
    "SecureReadingRoom",
    "HITLDecision",
    "ZeroLossContainment",
]

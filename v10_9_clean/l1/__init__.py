"""
L1 Cognition Layer — v10_9

Exports the public L1 planning API:
  • StrategyReasoner
  • RAGReasoner
  • DraftingReasoner
  • PlanObject (planning contract)
  • DEFAULT_FRAMING_PROFILE
  • META_PROFILE

Nothing in this layer may import from L2/L3/L4/L5.
This __init__ ensures clean, package-safe exposure of L1 functionality.
"""

from .l1_reasoning import (
    StrategyReasoner,
    RAGReasoner,
    DraftingReasoner,
)

from .plan_contracts import PlanObject

from .injection_profiles import DEFAULT_FRAMING_PROFILE
from .meta_profile import META_PROFILE

__all__ = [
    "StrategyReasoner",
    "RAGReasoner",
    "DraftingReasoner",
    "PlanObject",
    "DEFAULT_FRAMING_PROFILE",
    "META_PROFILE",
]

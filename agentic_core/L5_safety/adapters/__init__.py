"""
L5 Safety Adapters - Protocol-compliant wrappers for legacy implementations.

These adapters wrap existing L5 components to conform to the new interface protocols,
enabling gradual migration without breaking existing code.
"""

from .human_review_adapter import HumanReviewAdapter
from .verification_gate_adapter import VerificationGateAdapter

__all__ = [
    "VerificationGateAdapter",
    "HumanReviewAdapter",
]

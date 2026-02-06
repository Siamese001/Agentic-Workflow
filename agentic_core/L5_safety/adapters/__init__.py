"""
L5 Safety Adapters - Protocol-compliant wrappers for legacy implementations.

These adapters wrap existing L5 components to conform to the new interface protocols,
enabling gradual migration without breaking existing code.
"""

from .HumanReviewAdapter import HumanReviewAdapter
from .VerificationGateAdapter import VerificationGateAdapter

__all__ = [
    "VerificationGateAdapter",
    "HumanReviewAdapter",
]

"""Mock implementations for testing.

Phase 2 - Pillar 1: Layering Model
Provides simple mock implementations of core interfaces for unit testing.
"""

from .mock_cognitive_plane import MockCognitivePlane
from .mock_action_plane import MockActionPlane

__all__ = [
    "MockCognitivePlane",
    "MockActionPlane",
]

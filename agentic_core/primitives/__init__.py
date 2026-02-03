"""
Primitives module for agentic_core.

Provides foundational infrastructure for feature flags, dependency resolution,
and graceful degradation patterns.
"""

from .feature_flags import FeatureFlag, FeatureFlagManager
from .dependency_resolver import DynamicLoader

__all__ = [
    "FeatureFlag",
    "FeatureFlagManager",
    "DynamicLoader",
]

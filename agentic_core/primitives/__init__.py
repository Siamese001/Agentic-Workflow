"""
Primitives module for agentic_core.

Provides foundational infrastructure for feature flags, dependency resolution,
and graceful degradation patterns.
"""

from .dependency_resolver import DynamicLoader
from .feature_flags import FeatureFlag, FeatureFlagManager

__all__ = [
    "FeatureFlag",
    "FeatureFlagManager",
    "DynamicLoader",
]

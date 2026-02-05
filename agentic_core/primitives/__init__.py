"""
Primitives module for agentic_core.

Provides foundational infrastructure for feature flags, dependency resolution,
and graceful degradation patterns.

RE-EXPORT: All primitives files are in agentic_core.utils - this module re-exports for API stability.
"""

from agentic_core.utils.dependency_resolver import DynamicLoader
from agentic_core.utils.feature_flags import FeatureFlag, FeatureFlagManager

__all__ = [
    "FeatureFlag",
    "FeatureFlagManager",
    "DynamicLoader",
]

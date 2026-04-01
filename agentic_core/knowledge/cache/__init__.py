"""Cache Module.

Pipeline C Phase C4: Version-aware cache with multi-factor keys and freshness management.
"""

from .version_aware_cache import VersionAwareCache, CacheEntry
from .catalog_keymaker import CatalogKeymaker, CacheKey
from .policy_evaluator import PolicyEvaluator, FreshnessCheck
from .fast_terminal import FastTerminal

__all__ = [
    "VersionAwareCache",
    "CacheEntry",
    "CatalogKeymaker",
    "CacheKey",
    "PolicyEvaluator",
    "FreshnessCheck",
    "FastTerminal",
]

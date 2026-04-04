"""Cache Module.

Pipeline C Phase C4: Version-aware cache with multi-factor keys and freshness management.
"""

from .catalog_keymaker import CacheKey, CatalogKeymaker
from .fast_terminal import FastTerminal
from .policy_evaluator import FreshnessCheck, PolicyEvaluator
from .version_aware_cache import CacheEntry, VersionAwareCache

__all__ = [
    "VersionAwareCache",
    "CacheEntry",
    "CatalogKeymaker",
    "CacheKey",
    "PolicyEvaluator",
    "FreshnessCheck",
    "FastTerminal",
]

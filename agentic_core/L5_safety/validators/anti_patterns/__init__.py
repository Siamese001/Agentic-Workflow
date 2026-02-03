"""
Anti-Pattern Detection Module

Guardian integration for detecting and preventing Phase 2 landmine anti-patterns:
- Silent Swallower: Exception blocks that swallow errors
- Type Erasure: Functions returning untyped dict or Any
- Path Fragility: String-based path manipulation
- Magic Configuration: Hardcoded constants in business logic
- Global Mutation: Runtime sys.path or os.environ modifications
"""

from .base_detector import (
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

__all__ = [
    "AntiPatternDetector",
    "AntiPatternViolation",
    "EnforcementLevel",
]

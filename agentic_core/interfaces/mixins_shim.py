"""
agentic_core/interfaces/mixins.py

Sovereign mixin interface for apps_* consumption.

Re-exports HealerMixin and MetaLearningMixin so apps_* utility files
can import from the approved interface boundary rather than directly
from L5_safety or L1_cognition.

# Configuration constants

AUTHORITY CONSTRAINTS:
- Mixin re-exports only — no mutation authority granted
- Fallback stubs provided if optional deps not installed

USAGE (apps_*):
    from agentic_core.interfaces.mixins_shim import HealerMixin, MetaLearningMixin
"""

from __future__ import annotations

try:
    from agentic_core.L5_safety.validators.healing_mixin import HealerMixin
# guardian: allow-silent-swallow - optional dependency
except ImportError:

    class HealerMixin:  # type: ignore[no-redef]
        """Stub when healing_mixin optional deps are not installed."""


try:
    from agentic_core.L1_cognition.reasoning.meta_learning_mixin import MetaLearningMixin
except ImportError:

    class MetaLearningMixin:  # type: ignore[no-redef]
        """Stub when meta_learning_mixin optional deps are not installed."""


__all__ = [
    "HealerMixin",
    "MetaLearningMixin",
]

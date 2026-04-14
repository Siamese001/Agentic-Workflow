"""
agentic_core/interfaces/mixins.py

Sovereign mixin interface for apps_* consumption.

Re-exports HealerMixin and MetaLearningMixin so apps_* utility files
can import from the approved interface boundary rather than directly
from L5_safety or L1_cognition.

# Configuration constants

AUTHORITY CONSTRAINTS:
- Mixin re-exports only
- Missing optional dependencies fail fast with a clear error

USAGE (apps_*):
    from agentic_core.interfaces.mixins_shim import HealerMixin, MetaLearningMixin
"""

from __future__ import annotations


def _missing_dependency(name: str, target: str):
    class _MissingDependencyMixin:  # type: ignore[no-redef]
        """Fail-fast stub when an optional dependency is unavailable."""

        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError(f"{name} is unavailable because {target} could not be imported.")

    return _MissingDependencyMixin


try:
    from agentic_core.L5_safety.validators.healing_mixin import HealerMixin
except ImportError as exc:
    HealerMixin = _missing_dependency("HealerMixin", str(exc))

try:
    from agentic_core.L1_cognition.reasoning.meta_learning_mixin import MetaLearningMixin
except ImportError as exc:
    MetaLearningMixin = _missing_dependency("MetaLearningMixin", str(exc))

__all__ = ["HealerMixin", "MetaLearningMixin"]

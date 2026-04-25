"""
agentic_core/interfaces/mixins.py

Re-exports HealingPolicyMixin and MetaLearningMixin so apps_* utility files
can import from the approved interface boundary rather than reaching directly
into other layers.

AUTHORITY CONSTRAINTS:
- Mixin re-exports only.
- Missing optional dependencies fail fast with a clear error.

History:
- 2026-04-24 (W3 of mixin-mro-simplification-de1850): redirected
  ``HealerMixin`` (rename shim) to its canonical ``HealingPolicyMixin``.
  The previous import path (``agentic_core.L5_safety.validators.healing_mixin``)
  did not exist on disk, so this re-export was permanently in the
  ``_missing_dependency`` fallback. Same observation for the
  ``MetaLearningMixin`` import path.
"""

from __future__ import annotations


def _missing_dependency(name: str, target: str):
    class _MissingDependencyMixin:  # type: ignore[no-redef]
        """Fail-fast stub when an optional dependency is unavailable."""

        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError(f"{name} is unavailable because {target} could not be imported.")

    return _MissingDependencyMixin


try:
    from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
except ImportError as exc:  # guardian: allow-silent-swallow -- optional dependency
    HealingPolicyMixin = _missing_dependency("HealingPolicyMixin", str(exc))

# Backwards-compat alias for the in-flight rename. Existing call sites that
# still import ``HealerMixin`` from this module continue to work; new code
# should import ``HealingPolicyMixin`` directly.
HealerMixin = HealingPolicyMixin

try:
    from agentic_core.mixins.meta_learning_mixin import MetaLearningMixin
except ImportError as exc:  # guardian: allow-silent-swallow -- optional dependency
    MetaLearningMixin = _missing_dependency("MetaLearningMixin", str(exc))

__all__ = ["HealingPolicyMixin", "HealerMixin", "MetaLearningMixin"]

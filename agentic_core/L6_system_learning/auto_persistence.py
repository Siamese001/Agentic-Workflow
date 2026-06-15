"""Compatibility exports for runtime ADG auto-persistence.

The canonical implementation lives in
``agentic_core.L6_system_learning.runtime_adg.auto_persistence``.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.runtime_adg.auto_persistence import (
    AutoPersistenceTracingAdapter,
    get_auto_persistence_tracer,
)

__all__ = [
    "AutoPersistenceTracingAdapter",
    "get_auto_persistence_tracer",
]

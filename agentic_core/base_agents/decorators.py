"""
Shim module: re-exports decorator symbols from canonical locations.

54 files across L0–L6 import from ``agentic_core.base_agents.decorators``.
The actual implementation lives in ``agentic_core.L5_safety.utils.decorators_util``.

This shim exists solely to satisfy those imports without a 54-file mass-rename.
New code SHOULD import directly from the canonical location.

Canonical source: agentic_core/L5_safety/utils/decorators_util.py
Created: 2026-02-08 — Phantom-import resolution (Issue #5)
"""

from agentic_core.L5_safety.utils.decorators_util import (  # noqa: F401
    HEAL_RESULT_SCHEMA,
    standard_heal,
    standard_heal_async,
)

__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
]

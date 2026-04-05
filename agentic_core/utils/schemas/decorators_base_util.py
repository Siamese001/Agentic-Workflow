"""
Backward-compatibility shim for decorator imports.

DEPRECATED: Import from agentic_core.utils.decorators instead.
Canonical location: agentic_core/utils/decorators.py
"""

from __future__ import annotations

from agentic_core.utils.schemas.decorators_util import (  # noqa: F401
    HEAL_RESULT_SCHEMA,
    F,
    standard_heal,
    standard_heal_async,
)

__all__ = ["F", "HEAL_RESULT_SCHEMA", "standard_heal", "standard_heal_async"]

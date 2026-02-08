"""
Backward-compatibility shim for decorator imports.

DEPRECATED: Import from agentic_core.base_agents.decorators instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.base_agents.decorators import standard_heal, HEAL_RESULT_SCHEMA

Canonical location: agentic_core/base_agents/decorators.py
"""

from __future__ import annotations

from agentic_core.base_agents.decorators import (  # noqa: F401
    HEAL_RESULT_SCHEMA,
    standard_heal,
    standard_heal_async,
)

__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
]

"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.base_agents.timeout_decorator instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.base_agents.timeout_decorator import timeout

Canonical location: agentic_core/base_agents/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.base_agents.timeout_decorator import timeout  # noqa: F401

__all__ = [
    "timeout",
]

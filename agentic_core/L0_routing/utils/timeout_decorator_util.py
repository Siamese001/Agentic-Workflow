"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.utils.timeout_decorator_util instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.utils.timeout_decorator_util import timeout

Canonical location: agentic_core/base_agents/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout

__all__ = ["timeout", "TimeoutError"]

"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.L0_routing.utils.timeout_decorator instead.
Canonical location: agentic_core/L0_routing/utils/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.L0_routing.utils.timeout_decorator_util import timeout  # noqa: F401

__all__ = ["timeout"]

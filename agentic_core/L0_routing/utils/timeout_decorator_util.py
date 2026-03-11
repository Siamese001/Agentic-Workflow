"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.utils.timeout_decorator_util instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.utils.timeout_decorator_util import timeout

Canonical location: agentic_core/base_agents/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout  # noqa: F401

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = [
    "timeout",
    "TimeoutError",
]

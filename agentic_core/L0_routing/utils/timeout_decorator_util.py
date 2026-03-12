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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['timeout', 'TimeoutError']

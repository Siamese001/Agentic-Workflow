"""
Timeout decorator for execution time limits.

This module provides a timeout decorator to prevent functions from running
indefinitely. It's used across the agentic system for safety and reliability.
"""

from __future__ import annotations

from .timeout_decorator_impl_util import TimeoutError, timeout  # noqa: F401

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["timeout", "TimeoutError"]

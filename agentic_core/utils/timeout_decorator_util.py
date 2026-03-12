"""
Timeout decorator for execution time limits.

This module provides a timeout decorator to prevent functions from running
indefinitely. It's used across the agentic system for safety and reliability.
"""
from __future__ import annotations
from .timeout_decorator_impl_util import TimeoutError, timeout
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['timeout', 'TimeoutError']

"""
Timeout decorator for execution time limits.

This module provides a timeout decorator to prevent functions from running
indefinitely. It's used across the agentic system for safety and reliability.
"""

from __future__ import annotations

from .timeout_decorator_impl_util import TimeoutError, timeout

__all__ = ["timeout", "TimeoutError"]

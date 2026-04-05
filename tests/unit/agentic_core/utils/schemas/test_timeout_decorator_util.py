"""Foundational behavioral tests for agentic_core/utils/timeout_decorator_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module timeout_decorator_util must be importable."""
    from agentic_core.utils.schemas import timeout_decorator_util
    assert timeout_decorator_util is not None

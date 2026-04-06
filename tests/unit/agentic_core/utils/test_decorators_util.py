"""Foundational behavioral tests for agentic_core/utils/decorators_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module decorators_util must be importable."""
    from agentic_core.utils import decorators_util
    assert decorators_util is not None

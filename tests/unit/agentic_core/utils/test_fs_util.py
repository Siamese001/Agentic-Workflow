"""Foundational behavioral tests for agentic_core/utils/fs_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module fs_util must be importable."""
    from agentic_core.utils import fs_util
    assert fs_util is not None

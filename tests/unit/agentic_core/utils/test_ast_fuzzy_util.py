"""Foundational behavioral tests for agentic_core/utils/ast_fuzzy_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module ast_fuzzy_util must be importable."""
    from agentic_core.utils import ast_fuzzy_util
    assert ast_fuzzy_util is not None

"""Foundational behavioral tests for agentic_core/utils/ast_fuzzy_util.py."""

from __future__ import annotations


def test_module_importable():
    """Module ast_fuzzy_util must be importable."""
    from agentic_core.utils import ast_fuzzy_util

    assert ast_fuzzy_util is not None


def test_parse_ast_safe_happy_path():
    """parse_ast_safe must parse valid Python code."""
    from agentic_core.utils import ast_fuzzy_util

    source = "def foo(): return 42"
    result = ast_fuzzy_util.parse_ast_safe(source)
    assert result is not None
    assert hasattr(result, "body")


def test_parse_ast_safe_failure_path():
    """parse_ast_safe must return None for invalid syntax."""
    from agentic_core.utils import ast_fuzzy_util

    source = "def foo(: return 42"
    result = ast_fuzzy_util.parse_ast_safe(source)
    assert result is None


def test_parse_ast_safe_edge_case():
    """parse_ast_safe must handle empty string."""
    from agentic_core.utils import ast_fuzzy_util

    source = ""
    result = ast_fuzzy_util.parse_ast_safe(source)
    assert result is not None  # Empty module is valid AST

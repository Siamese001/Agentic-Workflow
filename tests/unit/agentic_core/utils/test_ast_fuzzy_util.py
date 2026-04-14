"""Foundational behavioral tests for agentic_core/utils/ast_fuzzy_util.py."""

from __future__ import annotations

import pytest


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


def test_read_threshold_from_env_valid_value(monkeypatch):
    """_read_threshold_from_env returns parsed float for valid env value."""
    monkeypatch.setenv("AST_FUZZY_THRESHOLD", "0.7")
    from agentic_core.utils.ast_fuzzy_util import _read_threshold_from_env

    result = _read_threshold_from_env()
    assert abs(result - 0.7) < 1e-9


def test_read_threshold_from_env_invalid_string_returns_default(monkeypatch):
    """_read_threshold_from_env falls back to default for non-float env value."""
    monkeypatch.setenv("AST_FUZZY_THRESHOLD", "not_a_float")
    from agentic_core.utils.ast_fuzzy_util import _DEFAULT_AST_FUZZY_THRESHOLD, _read_threshold_from_env

    assert _read_threshold_from_env() == _DEFAULT_AST_FUZZY_THRESHOLD


def test_read_threshold_from_env_out_of_range_returns_default(monkeypatch):
    """_read_threshold_from_env falls back to default when value > 1.0."""
    monkeypatch.setenv("AST_FUZZY_THRESHOLD", "1.5")
    from agentic_core.utils.ast_fuzzy_util import _DEFAULT_AST_FUZZY_THRESHOLD, _read_threshold_from_env

    assert _read_threshold_from_env() == _DEFAULT_AST_FUZZY_THRESHOLD


def test_read_threshold_from_env_unset_returns_default(monkeypatch):
    """_read_threshold_from_env returns default when env var is not set."""
    monkeypatch.delenv("AST_FUZZY_THRESHOLD", raising=False)
    from agentic_core.utils.ast_fuzzy_util import _DEFAULT_AST_FUZZY_THRESHOLD, _read_threshold_from_env

    assert _read_threshold_from_env() == _DEFAULT_AST_FUZZY_THRESHOLD

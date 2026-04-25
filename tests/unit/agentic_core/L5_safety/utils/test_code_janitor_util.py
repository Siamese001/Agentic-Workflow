"""Smoke tests for code_janitor_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_janitor_util")


def test_module_imports_clean():
    assert mod is not None


def test_CodeJanitor_present():
    assert hasattr(mod, "CodeJanitor")
    assert isinstance(mod.CodeJanitor, type)


def test_validate_syntax_callable():
    assert callable(mod.validate_syntax)

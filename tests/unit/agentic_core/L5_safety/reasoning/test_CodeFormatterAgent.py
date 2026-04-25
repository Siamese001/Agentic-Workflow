"""Smoke tests for CodeFormatterAgent — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.CodeFormatterAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_CodeFormatterAgent_class_present():
    assert hasattr(mod, "CodeFormatterAgent")
    assert isinstance(mod.CodeFormatterAgent, type)


def test_FormatResult_class_present():
    assert hasattr(mod, "FormatResult")
    assert isinstance(mod.FormatResult, type)

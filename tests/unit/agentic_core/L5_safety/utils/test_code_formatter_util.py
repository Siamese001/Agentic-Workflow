"""Smoke tests for code_formatter_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_formatter_util")


def test_module_imports_clean():
    assert mod is not None


def test_FormatResult_present():
    assert hasattr(mod, "FormatResult")
    assert isinstance(mod.FormatResult, type)


def test_format_file_callable():
    assert callable(mod.format_file)

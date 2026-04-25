"""Smoke tests for complexity_analyzer_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.complexity_analyzer_util")


def test_module_imports_clean():
    assert mod is not None


def test_ComplexityViolation_present():
    assert hasattr(mod, "ComplexityViolation")
    assert isinstance(mod.ComplexityViolation, type)


def test_calculate_cyclomatic_complexity_callable():
    assert callable(mod.calculate_cyclomatic_complexity)

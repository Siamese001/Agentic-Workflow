"""Smoke tests for ComplexityAnalyzerAgent — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_ComplexityAnalyzerAgent_class_present():
    assert hasattr(mod, "ComplexityAnalyzerAgent")
    assert isinstance(mod.ComplexityAnalyzerAgent, type)

"""Smoke tests for classification_core — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.file_classification.classification_core")


def test_module_imports_clean():
    assert mod is not None


def test_ClassificationResult_present():
    assert hasattr(mod, "ClassificationResult")
    assert isinstance(mod.ClassificationResult, type)


def test_ClassificationResult_instantiable():
    result = mod.ClassificationResult(
        file_type="agent",
        confidence=0.9,
        signals=["test_signal"],
        warnings=[],
    )
    assert result.file_type == "agent"
    assert result.confidence == 0.9


def test_ClassificationResult_has_execution_mode():
    result = mod.ClassificationResult(
        file_type="util",
        confidence=0.8,
        signals=[],
        warnings=[],
    )
    assert hasattr(result, "execution_mode")

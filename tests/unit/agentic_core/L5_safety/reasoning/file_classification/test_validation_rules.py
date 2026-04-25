"""Smoke tests for validation_rules — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.file_classification.validation_rules")


def test_module_imports_clean():
    assert mod is not None


def test_validate_layer_alignment_callable():
    assert callable(mod.validate_layer_alignment)


def test_Violation_present():
    assert hasattr(mod, "Violation")
    assert isinstance(mod.Violation, type)

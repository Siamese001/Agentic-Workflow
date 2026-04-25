"""Smoke tests for naming_policy — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.file_classification.naming_policy")


def test_module_imports_clean():
    assert mod is not None


def test_normalize_filename_callable():
    assert callable(mod.normalize_filename)


def test_get_compliant_name_callable():
    assert callable(mod.get_compliant_name)

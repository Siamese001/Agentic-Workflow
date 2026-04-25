"""Smoke tests for circular_import_fixer_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.circular_import_fixer_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_fix_imports_in_file_callable():
    assert callable(mod.fix_imports_in_file)


def test_calculate_relative_import_callable():
    assert callable(mod.calculate_relative_import)

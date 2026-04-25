"""Smoke tests for unified_cst_healer_util — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.unified_cst_healer_util")


def test_module_imports_clean():
    assert mod is not None


def test_create_bare_except_fixer_callable():
    assert callable(mod.create_bare_except_fixer)


def test_VerificationGate_present():
    assert hasattr(mod, "VerificationGate")

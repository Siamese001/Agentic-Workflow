"""Smoke tests for L5_safety adapters __init__ — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.adapters")


def test_module_imports_clean():
    assert mod is not None


def test_ApprovalHandle_present():
    assert hasattr(mod, "ApprovalHandle")
    assert isinstance(mod.ApprovalHandle, type)


def test_ApprovalOutcome_present():
    assert hasattr(mod, "ApprovalOutcome")
    assert isinstance(mod.ApprovalOutcome, type)

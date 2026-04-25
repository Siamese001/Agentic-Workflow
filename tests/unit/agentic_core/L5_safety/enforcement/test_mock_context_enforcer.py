"""Smoke tests for mock_context_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.mock_context_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_MockContext_present():
    assert hasattr(mod, "MockContext")
    assert isinstance(mod.MockContext, type)


def test_validate_l2_l3_structure_callable():
    assert callable(mod.validate_l2_l3_structure)

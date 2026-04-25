"""Smoke tests for critical_dual_enforcement_audit_enforcer — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.critical_dual_enforcement_audit_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_RequirementMetadata_present():
    assert hasattr(mod, "RequirementMetadata")
    assert isinstance(mod.RequirementMetadata, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)

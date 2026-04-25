"""Smoke tests for runtime_mutation_guard — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.runtime_mutation_guard")


def test_module_imports_clean():
    assert mod is not None


def test_RuntimeMutationViolation_present():
    assert hasattr(mod, "RuntimeMutationViolation")
    assert isinstance(mod.RuntimeMutationViolation, type)


def test_is_protected_module_callable():
    assert callable(mod.is_protected_module)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)

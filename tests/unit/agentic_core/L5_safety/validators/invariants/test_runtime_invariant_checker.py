"""Smoke tests for runtime_invariant_checker — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.invariants.runtime_invariant_checker")


def test_module_imports_clean():
    assert mod is not None


def test_C0AuthorityLeakError_class_present():
    assert hasattr(mod, "C0AuthorityLeakError")
    assert isinstance(mod.C0AuthorityLeakError, type)


def test_assert_mutation_source_is_l2_callable():
    assert callable(mod.assert_mutation_source_is_l2)

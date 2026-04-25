"""Smoke tests for SubAtomicAgent — wave 19."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.SubAtomicAgent")


def test_module_imports_clean():
    assert mod is not None


def test_SubAtomicImpl_class_present():
    assert hasattr(mod, "SubAtomicImpl")
    assert isinstance(mod.SubAtomicImpl, type)


def test_SubAtomicImpl_is_class():
    from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicImpl

    assert isinstance(SubAtomicImpl, type)

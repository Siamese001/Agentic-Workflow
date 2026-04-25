"""Smoke tests for run_state_authority — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.enforcement.authority.run_state_authority")


def test_module_imports_clean():
    assert mod is not None


def test_WriteGovernorMixin_class_present():
    assert hasattr(mod, "WriteGovernorMixin")
    assert isinstance(mod.WriteGovernorMixin, type)


def test_ExecutionProofEmitter_class_present():
    assert hasattr(mod, "ExecutionProofEmitter")
    assert isinstance(mod.ExecutionProofEmitter, type)


def test_ActorContext_class_present():
    assert hasattr(mod, "ActorContext")
    assert isinstance(mod.ActorContext, type)

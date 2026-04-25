"""Smoke tests for commit_versioned_state_transition — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.versioning.commit_versioned_state_transition")


def test_module_imports_clean():
    assert mod is not None


def test_ActorContext_class_present():
    assert hasattr(mod, "ActorContext")
    assert isinstance(mod.ActorContext, type)


def test_SnapshotPolicy_class_present():
    assert hasattr(mod, "SnapshotPolicy")
    assert isinstance(mod.SnapshotPolicy, type)


def test_StateConflictError_is_exception():
    assert issubclass(mod.StateConflictError, Exception)


def test_get_state_version_registry_callable():
    assert callable(mod.get_state_version_registry)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)

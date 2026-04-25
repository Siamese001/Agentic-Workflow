"""Smoke tests for credential_access_guard — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.security.credential_access_guard")


def test_module_imports_clean():
    assert mod is not None


def test_CredentialAccessDenied_present():
    assert hasattr(mod, "CredentialAccessDenied")
    assert isinstance(mod.CredentialAccessDenied, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)

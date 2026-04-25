"""Smoke tests for L5 credential_guard — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.credential_guard")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_CredentialGuard_class_present():
    assert hasattr(mod, "CredentialGuard")
    assert isinstance(mod.CredentialGuard, type)


def test_CredentialAccessDeniedError_is_exception():
    assert issubclass(mod.CredentialAccessDeniedError, Exception)


def test_get_credential_guard_callable():
    assert callable(mod.get_credential_guard)

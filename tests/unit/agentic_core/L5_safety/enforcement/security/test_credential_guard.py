"""Surface coverage for `agentic_core.L5_safety.enforcement.security.credential_guard`.

Wave 10 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). L5
credential exfiltration guard.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.security.credential_guard"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "CredentialGuard")
    assert inspect.isclass(mod.CredentialGuard)


@pytest.mark.parametrize(
    "fn", ["get_credential_guard", "is_text_file", "scan_file", "scan_repository", "main"]
)
def test_public_functions_callable(mod, fn):
    assert hasattr(mod, fn)
    assert callable(getattr(mod, fn))


def test_get_credential_guard_returns_instance(mod):
    guard = mod.get_credential_guard()
    assert guard is not None
    assert isinstance(guard, mod.CredentialGuard)

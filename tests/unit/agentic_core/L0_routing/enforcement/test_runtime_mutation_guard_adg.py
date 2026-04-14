"""Runtime-hardened tests for runtime mutation guard helpers."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestRuntimeMutationGuardContracts:
    def test_is_protected_module_returns_bool(self, enforcement_package, monkeypatch):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        assert isinstance(enforcement_package.is_protected_module("agentic_core.test"), bool)

    def test_is_protected_object_returns_bool(self, enforcement_package, monkeypatch):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        assert isinstance(enforcement_package.is_protected_object("test_string"), bool)

    def test_exception_and_guard_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.RuntimeMutationViolation(), Exception)
        assert enforcement_package.RuntimeMutationGuard() is not None

    def test_runtime_mutation_guard_install_does_not_raise_when_disabled(
        self, enforcement_package, monkeypatch
    ):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        guard = enforcement_package.RuntimeMutationGuard()

        guard.install()

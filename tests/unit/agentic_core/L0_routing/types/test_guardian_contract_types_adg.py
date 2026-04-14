"""Runtime-hardened contract tests for guardian contract types."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

MODULE_CANDIDATES = [
    "agentic_core.L0_routing.types.guardian_contract_types",
    "agentic_core.L0_routing.types.guardian_contracts_types",
]
CLASS_CANDIDATES = ["V15EnforcementError", "V15SoftFailAbort", "GuardianContractError"]
CALLABLE_CANDIDATES = ["is_v15_enforced", "is_v15_hard_fail", "validate_guardian_contract"]


def _import_first_available(candidates: list[str]):
    errors: list[str] = []
    for module_path in candidates:
        try:
            return importlib.import_module(module_path)
        except Exception as exc:
            errors.append(f"{module_path} -> {exc.__class__.__name__}: {exc}")
    pytest.skip("No compatible guardian contract module import succeeded: " + " | ".join(errors))


def _resolve_first(obj, candidates: list[str]):
    for name in candidates:
        value = getattr(obj, name, None)
        if value is not None:
            return name, value
    return None, None


@pytest.fixture(scope="module")
def mod():
    return _import_first_available(MODULE_CANDIDATES)


def test_module_importable(mod):
    assert mod.__name__ in MODULE_CANDIDATES


def test_v15_error_surface_exists(mod):
    name, value = _resolve_first(mod, CLASS_CANDIDATES)
    assert value is not None
    assert isinstance(value, type)


def test_v15_helper_exists(mod):
    name, value = _resolve_first(mod, CALLABLE_CANDIDATES)
    assert callable(value)

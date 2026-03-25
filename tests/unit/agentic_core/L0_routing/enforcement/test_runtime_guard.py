"""Behavioral contract tests for agentic_core.L0_routing.enforcement.runtime_guard."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.runtime_guard"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_typevar_is_instantiable(mod):
    """TypeVar is accessible and is a type."""
    cls = getattr(mod, "TypeVar", None)
    assert cls is not None, "TypeVar must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TypeVar must be a class"


def test_v15enforcementerror_is_instantiable(mod):
    """V15EnforcementError is accessible and is a type."""
    cls = getattr(mod, "V15EnforcementError", None)
    assert cls is not None, "V15EnforcementError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "V15EnforcementError must be a class"


def test_callable_is_callable(mod):
    """Callable is accessible and callable."""
    func = getattr(mod, "Callable", None)
    assert func is not None, "Callable must be defined in {MODULE_PATH}"
    assert callable(func), "Callable must be callable"


def test_assert_v15_guarded_is_callable(mod):
    """assert_v15_guarded is accessible and callable."""
    func = getattr(mod, "assert_v15_guarded", None)
    assert func is not None, "assert_v15_guarded must be defined in {MODULE_PATH}"
    assert callable(func), "assert_v15_guarded must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_is_v15_enforced_is_callable(mod):
    """is_v15_enforced is accessible and callable."""
    func = getattr(mod, "is_v15_enforced", None)
    assert func is not None, "is_v15_enforced must be defined in {MODULE_PATH}"
    assert callable(func), "is_v15_enforced must be callable"


def test_is_v15_hard_fail_is_callable(mod):
    """is_v15_hard_fail is accessible and callable."""
    func = getattr(mod, "is_v15_hard_fail", None)
    assert func is not None, "is_v15_hard_fail must be defined in {MODULE_PATH}"
    assert callable(func), "is_v15_hard_fail must be callable"


def test_runtime_guard_is_callable(mod):
    """runtime_guard is accessible and callable."""
    func = getattr(mod, "runtime_guard", None)
    assert func is not None, "runtime_guard must be defined in {MODULE_PATH}"
    assert callable(func), "runtime_guard must be callable"


def test_v15_runtime_boundary_is_callable(mod):
    """v15_runtime_boundary is accessible and callable."""
    func = getattr(mod, "v15_runtime_boundary", None)
    assert func is not None, "v15_runtime_boundary must be defined in {MODULE_PATH}"
    assert callable(func), "v15_runtime_boundary must be callable"


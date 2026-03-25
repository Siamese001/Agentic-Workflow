"""Behavioral contract tests for agentic_core.L0_routing.enforcement.runtime_mutation_guard."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.runtime_mutation_guard"


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


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_runtimemutationguard_is_instantiable(mod):
    """RuntimeMutationGuard is accessible and is a type."""
    cls = getattr(mod, "RuntimeMutationGuard", None)
    assert cls is not None, "RuntimeMutationGuard must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeMutationGuard must be a class"


def test_runtimemutationviolation_is_instantiable(mod):
    """RuntimeMutationViolation is accessible and is a type."""
    cls = getattr(mod, "RuntimeMutationViolation", None)
    assert cls is not None, "RuntimeMutationViolation must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeMutationViolation must be a class"


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


def test_get_mutation_guard_is_callable(mod):
    """get_mutation_guard is accessible and callable."""
    func = getattr(mod, "get_mutation_guard", None)
    assert func is not None, "get_mutation_guard must be defined in {MODULE_PATH}"
    assert callable(func), "get_mutation_guard must be callable"


def test_guard_function_replacement_is_callable(mod):
    """guard_function_replacement is accessible and callable."""
    func = getattr(mod, "guard_function_replacement", None)
    assert func is not None, "guard_function_replacement must be defined in {MODULE_PATH}"
    assert callable(func), "guard_function_replacement must be callable"


def test_guard_importlib_reload_is_callable(mod):
    """guard_importlib_reload is accessible and callable."""
    func = getattr(mod, "guard_importlib_reload", None)
    assert func is not None, "guard_importlib_reload must be defined in {MODULE_PATH}"
    assert callable(func), "guard_importlib_reload must be callable"


def test_guard_metaclass_creation_is_callable(mod):
    """guard_metaclass_creation is accessible and callable."""
    func = getattr(mod, "guard_metaclass_creation", None)
    assert func is not None, "guard_metaclass_creation must be defined in {MODULE_PATH}"
    assert callable(func), "guard_metaclass_creation must be callable"


def test_guard_setattr_is_callable(mod):
    """guard_setattr is accessible and callable."""
    func = getattr(mod, "guard_setattr", None)
    assert func is not None, "guard_setattr must be defined in {MODULE_PATH}"
    assert callable(func), "guard_setattr must be callable"


def test_install_runtime_mutation_guard_is_callable(mod):
    """install_runtime_mutation_guard is accessible and callable."""
    func = getattr(mod, "install_runtime_mutation_guard", None)
    assert func is not None, "install_runtime_mutation_guard must be defined in {MODULE_PATH}"
    assert callable(func), "install_runtime_mutation_guard must be callable"


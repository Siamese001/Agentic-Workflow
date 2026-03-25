"""Behavioral contract tests for agentic_core.L0_routing.enforcement.mutation_prohibition."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.mutation_prohibition"


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


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_protectedrootblockevent_is_instantiable(mod):
    """ProtectedRootBlockEvent is accessible and is a type."""
    cls = getattr(mod, "ProtectedRootBlockEvent", None)
    assert cls is not None, "ProtectedRootBlockEvent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProtectedRootBlockEvent must be a class"


def test_protectedrootpolicy_is_instantiable(mod):
    """ProtectedRootPolicy is accessible and is a type."""
    cls = getattr(mod, "ProtectedRootPolicy", None)
    assert cls is not None, "ProtectedRootPolicy must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProtectedRootPolicy must be a class"


def test_sourcemutationblocked_is_instantiable(mod):
    """SourceMutationBlocked is accessible and is a type."""
    cls = getattr(mod, "SourceMutationBlocked", None)
    assert cls is not None, "SourceMutationBlocked must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SourceMutationBlocked must be a class"


def test_datetime_is_instantiable(mod):
    """datetime is accessible and is a type."""
    cls = getattr(mod, "datetime", None)
    assert cls is not None, "datetime must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "datetime must be a class"


def test_timezone_is_instantiable(mod):
    """timezone is accessible and is a type."""
    cls = getattr(mod, "timezone", None)
    assert cls is not None, "timezone must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "timezone must be a class"


def test_generator_is_callable(mod):
    """Generator is accessible and callable."""
    func = getattr(mod, "Generator", None)
    assert func is not None, "Generator must be defined in {MODULE_PATH}"
    assert callable(func), "Generator must be callable"


def test_asdict_is_callable(mod):
    """asdict is accessible and callable."""
    func = getattr(mod, "asdict", None)
    assert func is not None, "asdict must be defined in {MODULE_PATH}"
    assert callable(func), "asdict must be callable"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


def test_contextmanager_is_callable(mod):
    """contextmanager is accessible and callable."""
    func = getattr(mod, "contextmanager", None)
    assert func is not None, "contextmanager must be defined in {MODULE_PATH}"
    assert callable(func), "contextmanager must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


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


def test_enforce_protected_root_is_callable(mod):
    """enforce_protected_root is accessible and callable."""
    func = getattr(mod, "enforce_protected_root", None)
    assert func is not None, "enforce_protected_root must be defined in {MODULE_PATH}"
    assert callable(func), "enforce_protected_root must be callable"


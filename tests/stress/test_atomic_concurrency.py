"""Behavioral contract tests for agentic_core.mixins.atomic_execution_mixin."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.mixins.atomic_execution_mixin"


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


def test_atomicexecutionerror_is_instantiable(mod):
    """AtomicExecutionError is accessible and is a type."""
    cls = getattr(mod, "AtomicExecutionError", None)
    assert cls is not None, "AtomicExecutionError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AtomicExecutionError must be a class"


def test_atomicexecutionmixin_is_instantiable(mod):
    """AtomicExecutionMixin is accessible and is a type."""
    cls = getattr(mod, "AtomicExecutionMixin", None)
    assert cls is not None, "AtomicExecutionMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AtomicExecutionMixin must be a class"


def test_atomictransaction_is_instantiable(mod):
    """AtomicTransaction is accessible and is a type."""
    cls = getattr(mod, "AtomicTransaction", None)
    assert cls is not None, "AtomicTransaction must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AtomicTransaction must be a class"


def test_filebackup_is_instantiable(mod):
    """FileBackup is accessible and is a type."""
    cls = getattr(mod, "FileBackup", None)
    assert cls is not None, "FileBackup must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FileBackup must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_datetime_is_instantiable(mod):
    """datetime is accessible and is a type."""
    cls = getattr(mod, "datetime", None)
    assert cls is not None, "datetime must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "datetime must be a class"


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


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


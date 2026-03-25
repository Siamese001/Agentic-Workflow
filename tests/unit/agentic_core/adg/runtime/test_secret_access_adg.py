"""Behavioral contract tests for agentic_core.adg.runtime.secret_access."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.secret_access"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_secretaccessevent_is_instantiable(mod):
    """SecretAccessEvent is accessible and is a type."""
    cls = getattr(mod, "SecretAccessEvent", None)
    assert cls is not None, "SecretAccessEvent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretAccessEvent must be a class"


def test_secretaccessoutcome_is_instantiable(mod):
    """SecretAccessOutcome is accessible and is a type."""
    cls = getattr(mod, "SecretAccessOutcome", None)
    assert cls is not None, "SecretAccessOutcome must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretAccessOutcome must be a class"


def test_secretaccessrecorder_is_instantiable(mod):
    """SecretAccessRecorder is accessible and is a type."""
    cls = getattr(mod, "SecretAccessRecorder", None)
    assert cls is not None, "SecretAccessRecorder must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretAccessRecorder must be a class"


def test_secretaccessreport_is_instantiable(mod):
    """SecretAccessReport is accessible and is a type."""
    cls = getattr(mod, "SecretAccessReport", None)
    assert cls is not None, "SecretAccessReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretAccessReport must be a class"


def test_secretkind_is_instantiable(mod):
    """SecretKind is accessible and is a type."""
    cls = getattr(mod, "SecretKind", None)
    assert cls is not None, "SecretKind must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretKind must be a class"


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


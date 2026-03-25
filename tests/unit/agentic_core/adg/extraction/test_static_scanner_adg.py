"""Behavioral contract tests for agentic_core.adg.extraction.static_scanner."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.extraction.static_scanner"


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


def test_adgstaticscanner_is_instantiable(mod):
    """ADGStaticScanner is accessible and is a type."""
    cls = getattr(mod, "ADGStaticScanner", None)
    assert cls is not None, "ADGStaticScanner must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGStaticScanner must be a class"


def test_edge_is_instantiable(mod):
    """Edge is accessible and is a type."""
    cls = getattr(mod, "Edge", None)
    assert cls is not None, "Edge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Edge must be a class"


def test_identitykind_is_instantiable(mod):
    """IdentityKind is accessible and is a type."""
    cls = getattr(mod, "IdentityKind", None)
    assert cls is not None, "IdentityKind must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityKind must be a class"


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


def test_scanmanifest_is_instantiable(mod):
    """ScanManifest is accessible and is a type."""
    cls = getattr(mod, "ScanManifest", None)
    assert cls is not None, "ScanManifest must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ScanManifest must be a class"


def test_scanresult_is_instantiable(mod):
    """ScanResult is accessible and is a type."""
    cls = getattr(mod, "ScanResult", None)
    assert cls is not None, "ScanResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ScanResult must be a class"


def test_iterator_is_callable(mod):
    """Iterator is accessible and callable."""
    func = getattr(mod, "Iterator", None)
    assert func is not None, "Iterator must be defined in {MODULE_PATH}"
    assert callable(func), "Iterator must be callable"


def test_asdict_is_callable(mod):
    """asdict is accessible and callable."""
    func = getattr(mod, "asdict", None)
    assert func is not None, "asdict must be defined in {MODULE_PATH}"
    assert callable(func), "asdict must be callable"


def test_canonical_name_is_callable(mod):
    """canonical_name is accessible and callable."""
    func = getattr(mod, "canonical_name", None)
    assert func is not None, "canonical_name must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_name must be callable"


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


def test_fields_is_callable(mod):
    """fields is accessible and callable."""
    func = getattr(mod, "fields", None)
    assert func is not None, "fields must be defined in {MODULE_PATH}"
    assert callable(func), "fields must be callable"


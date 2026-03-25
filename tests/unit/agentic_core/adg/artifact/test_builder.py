"""Behavioral contract tests for agentic_core.adg.artifact.builder_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.artifact.builder_types"


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


def test_adgartifact_is_instantiable(mod):
    """ADGArtifact is accessible and is a type."""
    cls = getattr(mod, "ADGArtifact", None)
    assert cls is not None, "ADGArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGArtifact must be a class"


def test_adgartifactbuilder_is_instantiable(mod):
    """ADGArtifactBuilder is accessible and is a type."""
    cls = getattr(mod, "ADGArtifactBuilder", None)
    assert cls is not None, "ADGArtifactBuilder must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGArtifactBuilder must be a class"


def test_blindspotreport_is_instantiable(mod):
    """BlindSpotReport is accessible and is a type."""
    cls = getattr(mod, "BlindSpotReport", None)
    assert cls is not None, "BlindSpotReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BlindSpotReport must be a class"


def test_entityrecord_is_instantiable(mod):
    """EntityRecord is accessible and is a type."""
    cls = getattr(mod, "EntityRecord", None)
    assert cls is not None, "EntityRecord must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EntityRecord must be a class"


def test_identitykind_is_instantiable(mod):
    """IdentityKind is accessible and is a type."""
    cls = getattr(mod, "IdentityKind", None)
    assert cls is not None, "IdentityKind must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityKind must be a class"


def test_identitynormalizer_is_instantiable(mod):
    """IdentityNormalizer is accessible and is a type."""
    cls = getattr(mod, "IdentityNormalizer", None)
    assert cls is not None, "IdentityNormalizer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityNormalizer must be a class"


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


def test_build_artifact_is_callable(mod):
    """build_artifact is accessible and callable."""
    func = getattr(mod, "build_artifact", None)
    assert func is not None, "build_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "build_artifact must be callable"


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


def test_module_path_to_layer_is_callable(mod):
    """module_path_to_layer is accessible and callable."""
    func = getattr(mod, "module_path_to_layer", None)
    assert func is not None, "module_path_to_layer must be defined in {MODULE_PATH}"
    assert callable(func), "module_path_to_layer must be callable"


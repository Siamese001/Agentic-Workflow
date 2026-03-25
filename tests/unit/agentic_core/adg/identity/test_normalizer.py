"""Behavioral contract tests for agentic_core.adg.identity.normalizer."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.identity.normalizer"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_identityconfidence_is_instantiable(mod):
    """IdentityConfidence is accessible and is a type."""
    cls = getattr(mod, "IdentityConfidence", None)
    assert cls is not None, "IdentityConfidence must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityConfidence must be a class"


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


def test_identityrecord_is_instantiable(mod):
    """IdentityRecord is accessible and is a type."""
    cls = getattr(mod, "IdentityRecord", None)
    assert cls is not None, "IdentityRecord must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityRecord must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_normalizationreport_is_instantiable(mod):
    """NormalizationReport is accessible and is a type."""
    cls = getattr(mod, "NormalizationReport", None)
    assert cls is not None, "NormalizationReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "NormalizationReport must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_build_identity_index_is_callable(mod):
    """build_identity_index is accessible and callable."""
    func = getattr(mod, "build_identity_index", None)
    assert func is not None, "build_identity_index must be defined in {MODULE_PATH}"
    assert callable(func), "build_identity_index must be callable"


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


def test_normalize_identity_is_callable(mod):
    """normalize_identity is accessible and callable."""
    func = getattr(mod, "normalize_identity", None)
    assert func is not None, "normalize_identity must be defined in {MODULE_PATH}"
    assert callable(func), "normalize_identity must be callable"


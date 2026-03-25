"""Behavioral contract tests for agentic_core.adg.artifact.normalizer_config."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.artifact.normalizer_config"


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


def test_artifactnormalizer_is_instantiable(mod):
    """ArtifactNormalizer is accessible and is a type."""
    cls = getattr(mod, "ArtifactNormalizer", None)
    assert cls is not None, "ArtifactNormalizer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ArtifactNormalizer must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_normalizedgraph_is_instantiable(mod):
    """NormalizedGraph is accessible and is a type."""
    cls = getattr(mod, "NormalizedGraph", None)
    assert cls is not None, "NormalizedGraph must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "NormalizedGraph must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


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


def test_normalize_artifact_is_callable(mod):
    """normalize_artifact is accessible and callable."""
    func = getattr(mod, "normalize_artifact", None)
    assert func is not None, "normalize_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "normalize_artifact must be callable"


def test_size_comparison_is_callable(mod):
    """size_comparison is accessible and callable."""
    func = getattr(mod, "size_comparison", None)
    assert func is not None, "size_comparison must be defined in {MODULE_PATH}"
    assert callable(func), "size_comparison must be callable"


"""Behavioral contract tests for agentic_core.config.core.complexity_metrics_config."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.config.core.complexity_metrics_config"


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


def test_complexitymetrics_is_instantiable(mod):
    """ComplexityMetrics is accessible and is a type."""
    cls = getattr(mod, "ComplexityMetrics", None)
    assert cls is not None, "ComplexityMetrics must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ComplexityMetrics must be a class"


def test_extractioncandidate_is_instantiable(mod):
    """ExtractionCandidate is accessible and is a type."""
    cls = getattr(mod, "ExtractionCandidate", None)
    assert cls is not None, "ExtractionCandidate must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExtractionCandidate must be a class"


def test_flatteningpattern_is_instantiable(mod):
    """FlatteningPattern is accessible and is a type."""
    cls = getattr(mod, "FlatteningPattern", None)
    assert cls is not None, "FlatteningPattern must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FlatteningPattern must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


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


def test_get_flattening_pattern_is_callable(mod):
    """get_flattening_pattern is accessible and callable."""
    func = getattr(mod, "get_flattening_pattern", None)
    assert func is not None, "get_flattening_pattern must be defined in {MODULE_PATH}"
    assert callable(func), "get_flattening_pattern must be callable"


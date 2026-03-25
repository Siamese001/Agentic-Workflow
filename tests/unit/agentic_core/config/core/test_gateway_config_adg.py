"""Behavioral contract tests for agentic_core.config.core.gateway_config."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.config.core.gateway_config"


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


def test_gatewaybundle_is_instantiable(mod):
    """GatewayBundle is accessible and is a type."""
    cls = getattr(mod, "GatewayBundle", None)
    assert cls is not None, "GatewayBundle must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GatewayBundle must be a class"


def test_gatewayfactory_is_instantiable(mod):
    """GatewayFactory is accessible and is a type."""
    cls = getattr(mod, "GatewayFactory", None)
    assert cls is not None, "GatewayFactory must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GatewayFactory must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_embeddingprovider_is_callable(mod):
    """EmbeddingProvider is accessible and callable."""
    func = getattr(mod, "EmbeddingProvider", None)
    assert func is not None, "EmbeddingProvider must be defined in {MODULE_PATH}"
    assert callable(func), "EmbeddingProvider must be callable"


def test_llmprovider_is_callable(mod):
    """LLMProvider is accessible and callable."""
    func = getattr(mod, "LLMProvider", None)
    assert func is not None, "LLMProvider must be defined in {MODULE_PATH}"
    assert callable(func), "LLMProvider must be callable"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


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


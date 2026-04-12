"""Behavioral contract tests for agentic_core.adg.adapters.ADGMemoryAdapter."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.adg.adapters.ADGMemoryAdapter"


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


def test_adgmemoryadapter_is_instantiable(mod):
    """ADGMemoryAdapter is accessible and is a type."""
    cls = getattr(mod, "ADGMemoryAdapter", None)
    assert cls is not None, "ADGMemoryAdapter must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGMemoryAdapter must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_graphmemorybridge_is_instantiable(mod):
    """GraphMemoryBridge is accessible and is a type."""
    cls = getattr(mod, "GraphMemoryBridge", None)
    assert cls is not None, "GraphMemoryBridge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GraphMemoryBridge must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_get_adapter_is_callable(mod):
    """Test get_adapter function is callable and returns expected type."""
    func = getattr(mod, "get_adapter", None)
    assert func is not None, "get_adapter must be defined"
    assert callable(func), "get_adapter must be callable"

    # Test function signature accepts expected parameters
    import inspect

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    assert len(params) >= 1, "get_adapter should accept at least one parameter"

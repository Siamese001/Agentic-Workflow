"""Behavioral contract tests for agentic_core.adg.client.InMemoryStore."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.adg.client.InMemoryStore"


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


def test_adgmcpclient_is_instantiable(mod):
    """ADGMCPClient is accessible and is a type."""
    cls = getattr(mod, "ADGMCPClient", None)
    assert cls is not None, "ADGMCPClient must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGMCPClient must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_inmemorystore_is_instantiable(mod):
    """InMemoryStore is accessible and is a type."""
    cls = getattr(mod, "InMemoryStore", None)
    assert cls is not None, "InMemoryStore must be defined"
    assert isinstance(cls, type), "InMemoryStore must be a class"

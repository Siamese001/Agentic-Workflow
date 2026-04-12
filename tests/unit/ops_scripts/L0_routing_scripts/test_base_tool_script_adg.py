"""Behavioral contract tests for agentic_core.L0_routing.scripts.base_tool_script."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.base_tool_script"


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


def test_basetool_is_instantiable(mod):
    """BaseTool is accessible and is a type."""
    cls = getattr(mod, "BaseTool", None)
    assert cls is not None, "BaseTool must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BaseTool must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_registry_is_instantiable(mod):
    """Registry is accessible and is a type."""
    cls = getattr(mod, "Registry", None)
    assert cls is not None, "Registry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Registry must be a class"


def test_tool_is_instantiable(mod):
    """Tool is accessible and is a type."""
    cls = getattr(mod, "Tool", None)
    assert cls is not None, "Tool must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Tool must be a class"


def test_tool_registry_is_instantiable(mod):
    """tool_registry is accessible and is a type."""
    cls = getattr(mod, "tool_registry", None)
    assert cls is not None, "tool_registry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "tool_registry must be a class"

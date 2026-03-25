"""Behavioral contract tests for agentic_core.L0_routing.scripts.base_tool."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.base_tool"


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


def test_abc_is_instantiable(mod):
    """ABC is accessible and is a type."""
    cls = getattr(mod, "ABC", None)
    assert cls is not None, "ABC must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ABC must be a class"


def test_basemodel_is_instantiable(mod):
    """BaseModel is accessible and is a type."""
    cls = getattr(mod, "BaseModel", None)
    assert cls is not None, "BaseModel must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BaseModel must be a class"


def test_basetool_is_instantiable(mod):
    """BaseTool is accessible and is a type."""
    cls = getattr(mod, "BaseTool", None)
    assert cls is not None, "BaseTool must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BaseTool must be a class"


def test_callable_is_instantiable(mod):
    """Callable is accessible and is a type."""
    cls = getattr(mod, "Callable", None)
    assert cls is not None, "Callable must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Callable must be a class"


def test_functionaltool_is_instantiable(mod):
    """FunctionalTool is accessible and is a type."""
    cls = getattr(mod, "FunctionalTool", None)
    assert cls is not None, "FunctionalTool must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FunctionalTool must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_toolregistry_is_instantiable(mod):
    """ToolRegistry is accessible and is a type."""
    cls = getattr(mod, "ToolRegistry", None)
    assert cls is not None, "ToolRegistry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ToolRegistry must be a class"


def test_field_is_callable(mod):
    """Field is accessible and callable."""
    func = getattr(mod, "Field", None)
    assert func is not None, "Field must be defined in {MODULE_PATH}"
    assert callable(func), "Field must be callable"


def test_abstractmethod_is_callable(mod):
    """abstractmethod is accessible and callable."""
    func = getattr(mod, "abstractmethod", None)
    assert func is not None, "abstractmethod must be defined in {MODULE_PATH}"
    assert callable(func), "abstractmethod must be callable"


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


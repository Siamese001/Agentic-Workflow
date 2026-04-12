"""Behavioral contract tests for agentic_core.L5_safety.config.structure_blueprint."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L5_safety.config.structure_blueprint"


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


def test_subfolderdefinition_is_instantiable(mod):
    """SubfolderDefinition is accessible and is a type."""
    cls = getattr(mod, "SubfolderDefinition", None)
    assert cls is not None, "SubfolderDefinition must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SubfolderDefinition must be a class"


def test_territorydefinition_is_instantiable(mod):
    """TerritoryDefinition is accessible and is a type."""
    cls = getattr(mod, "TerritoryDefinition", None)
    assert cls is not None, "TerritoryDefinition must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TerritoryDefinition must be a class"


def test_get_core_subfolder_map(mod):
    """Test get_core_subfolder_map runtime behavior."""
    result = mod.get_core_subfolder_map()
    assert result is not None, "get_core_subfolder_map should return a result"
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "adg" in result, "Result should contain 'adg' key"
    assert "L0_routing" in result, "Result should contain 'L0_routing' key"

"""Behavioral contract tests for agentic_core.base_agents.L1CognitionBase."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.base_agents.L1CognitionBase"


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


def test_l1cognitionbase_is_instantiable(mod):
    """L1CognitionBase is accessible and is a type."""
    cls = getattr(mod, "L1CognitionBase", None)
    assert cls is not None, "L1CognitionBase must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "L1CognitionBase must be a class"


def test_sovereignbaseagent_is_instantiable(mod):
    """SovereignBaseAgent is accessible and is a type."""
    cls = getattr(mod, "SovereignBaseAgent", None)
    assert cls is not None, "SovereignBaseAgent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SovereignBaseAgent must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


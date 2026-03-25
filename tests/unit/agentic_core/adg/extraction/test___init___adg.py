"""Behavioral contract tests for agentic_core.adg.extraction.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.extraction.__init__"


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


def test_adgstaticscanner_is_instantiable(mod):
    """ADGStaticScanner is accessible and is a type."""
    cls = getattr(mod, "ADGStaticScanner", None)
    assert cls is not None, "ADGStaticScanner must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGStaticScanner must be a class"


def test_agentregistryedge_is_instantiable(mod):
    """AgentRegistryEdge is accessible and is a type."""
    cls = getattr(mod, "AgentRegistryEdge", None)
    assert cls is not None, "AgentRegistryEdge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentRegistryEdge must be a class"


def test_agentregistryresult_is_instantiable(mod):
    """AgentRegistryResult is accessible and is a type."""
    cls = getattr(mod, "AgentRegistryResult", None)
    assert cls is not None, "AgentRegistryResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentRegistryResult must be a class"


def test_edge_is_instantiable(mod):
    """Edge is accessible and is a type."""
    cls = getattr(mod, "Edge", None)
    assert cls is not None, "Edge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Edge must be a class"


def test_scanresult_is_instantiable(mod):
    """ScanResult is accessible and is a type."""
    cls = getattr(mod, "ScanResult", None)
    assert cls is not None, "ScanResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ScanResult must be a class"


def test_scan_agent_registry_is_callable(mod):
    """scan_agent_registry is accessible and callable."""
    func = getattr(mod, "scan_agent_registry", None)
    assert func is not None, "scan_agent_registry must be defined in {MODULE_PATH}"
    assert callable(func), "scan_agent_registry must be callable"


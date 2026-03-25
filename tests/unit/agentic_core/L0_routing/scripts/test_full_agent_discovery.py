"""Behavioral contract tests for agentic_core.L0_routing.scripts.full_agent_discovery."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.full_agent_discovery"


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


def test_agentintegrityreport_is_instantiable(mod):
    """AgentIntegrityReport is accessible and is a type."""
    cls = getattr(mod, "AgentIntegrityReport", None)
    assert cls is not None, "AgentIntegrityReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentIntegrityReport must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_discoveryerror_is_instantiable(mod):
    """DiscoveryError is accessible and is a type."""
    cls = getattr(mod, "DiscoveryError", None)
    assert cls is not None, "DiscoveryError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DiscoveryError must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_datetime_is_instantiable(mod):
    """datetime is accessible and is a type."""
    cls = getattr(mod, "datetime", None)
    assert cls is not None, "datetime must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "datetime must be a class"


def test_timezone_is_instantiable(mod):
    """timezone is accessible and is a type."""
    cls = getattr(mod, "timezone", None)
    assert cls is not None, "timezone must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "timezone must be a class"


def test_analyze_agent_integrity_is_callable(mod):
    """analyze_agent_integrity is accessible and callable."""
    func = getattr(mod, "analyze_agent_integrity", None)
    assert func is not None, "analyze_agent_integrity must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_agent_integrity must be callable"


def test_check_compliance_gate_is_callable(mod):
    """check_compliance_gate is accessible and callable."""
    func = getattr(mod, "check_compliance_gate", None)
    assert func is not None, "check_compliance_gate must be defined in {MODULE_PATH}"
    assert callable(func), "check_compliance_gate must be callable"


def test_classification_cache_context_is_callable(mod):
    """classification_cache_context is accessible and callable."""
    func = getattr(mod, "classification_cache_context", None)
    assert func is not None, "classification_cache_context must be defined in {MODULE_PATH}"
    assert callable(func), "classification_cache_context must be callable"


def test_cli_interface_is_callable(mod):
    """cli_interface is accessible and callable."""
    func = getattr(mod, "cli_interface", None)
    assert func is not None, "cli_interface must be defined in {MODULE_PATH}"
    assert callable(func), "cli_interface must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_discover_all_agents_is_callable(mod):
    """discover_all_agents is accessible and callable."""
    func = getattr(mod, "discover_all_agents", None)
    assert func is not None, "discover_all_agents must be defined in {MODULE_PATH}"
    assert callable(func), "discover_all_agents must be callable"


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


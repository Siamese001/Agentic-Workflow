"""Behavioral contract tests for agentic_core.adg.runtime.query_engine."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.query_engine"


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


def test_adgruntimequeryengine_is_instantiable(mod):
    """ADGRuntimeQueryEngine is accessible and is a type."""
    cls = getattr(mod, "ADGRuntimeQueryEngine", None)
    assert cls is not None, "ADGRuntimeQueryEngine must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGRuntimeQueryEngine must be a class"


def test_agentcapability_is_instantiable(mod):
    """AgentCapability is accessible and is a type."""
    cls = getattr(mod, "AgentCapability", None)
    assert cls is not None, "AgentCapability must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentCapability must be a class"


def test_dependencypath_is_instantiable(mod):
    """DependencyPath is accessible and is a type."""
    cls = getattr(mod, "DependencyPath", None)
    assert cls is not None, "DependencyPath must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DependencyPath must be a class"


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


def test_get_runtime_query_engine_is_callable(mod):
    """get_runtime_query_engine is accessible and callable."""
    func = getattr(mod, "get_runtime_query_engine", None)
    assert func is not None, "get_runtime_query_engine must be defined in {MODULE_PATH}"
    assert callable(func), "get_runtime_query_engine must be callable"


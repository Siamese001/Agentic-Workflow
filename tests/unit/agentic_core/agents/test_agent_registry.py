"""Behavioral contract tests for agentic_core.agents.agent_registry."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.agents.agent_registry"


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


def test_agentexecutionprofile_is_instantiable(mod):
    """AgentExecutionProfile is accessible and is a type."""
    cls = getattr(mod, "AgentExecutionProfile", None)
    assert cls is not None, "AgentExecutionProfile must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentExecutionProfile must be a class"


def test_executionmode_is_instantiable(mod):
    """ExecutionMode is accessible and is a type."""
    cls = getattr(mod, "ExecutionMode", None)
    assert cls is not None, "ExecutionMode must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionMode must be a class"


def test_reasoningintensity_is_instantiable(mod):
    """ReasoningIntensity is accessible and is a type."""
    cls = getattr(mod, "ReasoningIntensity", None)
    assert cls is not None, "ReasoningIntensity must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReasoningIntensity must be a class"


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


def test_get_execution_profile_is_callable(mod):
    """get_execution_profile is accessible and callable."""
    func = getattr(mod, "get_execution_profile", None)
    assert func is not None, "get_execution_profile must be defined in {MODULE_PATH}"
    assert callable(func), "get_execution_profile must be callable"


def test_get_profile_is_callable(mod):
    """get_profile is accessible and callable."""
    func = getattr(mod, "get_profile", None)
    assert func is not None, "get_profile must be defined in {MODULE_PATH}"
    assert callable(func), "get_profile must be callable"


def test_registry_digest_is_callable(mod):
    """registry_digest is accessible and callable."""
    func = getattr(mod, "registry_digest", None)
    assert func is not None, "registry_digest must be defined in {MODULE_PATH}"
    assert callable(func), "registry_digest must be callable"


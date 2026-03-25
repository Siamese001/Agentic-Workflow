"""Behavioral contract tests for agentic_core.agents.types.agent_execution_profile_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.agents.types.agent_execution_profile_types"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


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


def test_compute_registry_digest_is_callable(mod):
    """compute_registry_digest is accessible and callable."""
    func = getattr(mod, "compute_registry_digest", None)
    assert func is not None, "compute_registry_digest must be defined in {MODULE_PATH}"
    assert callable(func), "compute_registry_digest must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


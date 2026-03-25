"""Behavioral contract tests for agentic_core.base_agents.L2ExecutionBase."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.base_agents.L2ExecutionBase"


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


def test_l2executionbase_is_instantiable(mod):
    """L2ExecutionBase is accessible and is a type."""
    cls = getattr(mod, "L2ExecutionBase", None)
    assert cls is not None, "L2ExecutionBase must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "L2ExecutionBase must be a class"


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


def test_runtime_guard_is_callable(mod):
    """runtime_guard is accessible and callable."""
    func = getattr(mod, "runtime_guard", None)
    assert func is not None, "runtime_guard must be defined in {MODULE_PATH}"
    assert callable(func), "runtime_guard must be callable"


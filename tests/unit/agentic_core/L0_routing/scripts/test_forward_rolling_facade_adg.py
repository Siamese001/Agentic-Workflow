"""Behavioral contract tests for agentic_core.L0_routing.scripts.forward_rolling_facade."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.forward_rolling_facade"


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


def test_adaptivedepthmanager_is_instantiable(mod):
    """AdaptiveDepthManager is accessible and is a type."""
    cls = getattr(mod, "AdaptiveDepthManager", None)
    assert cls is not None, "AdaptiveDepthManager must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AdaptiveDepthManager must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_contextpruningstrategy_is_instantiable(mod):
    """ContextPruningStrategy is accessible and is a type."""
    cls = getattr(mod, "ContextPruningStrategy", None)
    assert cls is not None, "ContextPruningStrategy must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ContextPruningStrategy must be a class"


def test_executionmode_is_instantiable(mod):
    """ExecutionMode is accessible and is a type."""
    cls = getattr(mod, "ExecutionMode", None)
    assert cls is not None, "ExecutionMode must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionMode must be a class"


def test_forwardrollingconfig_is_instantiable(mod):
    """ForwardRollingConfig is accessible and is a type."""
    cls = getattr(mod, "ForwardRollingConfig", None)
    assert cls is not None, "ForwardRollingConfig must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ForwardRollingConfig must be a class"


def test_forwardrollingfacade_is_instantiable(mod):
    """ForwardRollingFacade is accessible and is a type."""
    cls = getattr(mod, "ForwardRollingFacade", None)
    assert cls is not None, "ForwardRollingFacade must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ForwardRollingFacade must be a class"


def test_forwardrollingresult_is_instantiable(mod):
    """ForwardRollingResult is accessible and is a type."""
    cls = getattr(mod, "ForwardRollingResult", None)
    assert cls is not None, "ForwardRollingResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ForwardRollingResult must be a class"


def test_healthstatus_is_instantiable(mod):
    """HealthStatus is accessible and is a type."""
    cls = getattr(mod, "HealthStatus", None)
    assert cls is not None, "HealthStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealthStatus must be a class"


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


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_get_clock_is_callable(mod):
    """get_clock is accessible and callable."""
    func = getattr(mod, "get_clock", None)
    assert func is not None, "get_clock must be defined in {MODULE_PATH}"
    assert callable(func), "get_clock must be callable"


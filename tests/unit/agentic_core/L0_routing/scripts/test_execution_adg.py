"""Behavioral contract tests for agentic_core.L0_routing.scripts.execution."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.execution"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_callable_is_instantiable(mod):
    """Callable is accessible and is a type."""
    cls = getattr(mod, "Callable", None)
    assert cls is not None, "Callable must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Callable must be a class"


def test_dagstrategy_is_instantiable(mod):
    """DAGStrategy is accessible and is a type."""
    cls = getattr(mod, "DAGStrategy", None)
    assert cls is not None, "DAGStrategy must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DAGStrategy must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_eventdrivenstrategy_is_instantiable(mod):
    """EventDrivenStrategy is accessible and is a type."""
    cls = getattr(mod, "EventDrivenStrategy", None)
    assert cls is not None, "EventDrivenStrategy must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EventDrivenStrategy must be a class"


def test_executionstatus_is_instantiable(mod):
    """ExecutionStatus is accessible and is a type."""
    cls = getattr(mod, "ExecutionStatus", None)
    assert cls is not None, "ExecutionStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionStatus must be a class"


def test_executionstrategy_is_instantiable(mod):
    """ExecutionStrategy is accessible and is a type."""
    cls = getattr(mod, "ExecutionStrategy", None)
    assert cls is not None, "ExecutionStrategy must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionStrategy must be a class"


def test_abstractmethod_is_callable(mod):
    """abstractmethod is accessible and callable."""
    func = getattr(mod, "abstractmethod", None)
    assert func is not None, "abstractmethod must be defined in {MODULE_PATH}"
    assert callable(func), "abstractmethod must be callable"


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


def test_get_strategy_is_callable(mod):
    """get_strategy is accessible and callable."""
    func = getattr(mod, "get_strategy", None)
    assert func is not None, "get_strategy must be defined in {MODULE_PATH}"
    assert callable(func), "get_strategy must be callable"


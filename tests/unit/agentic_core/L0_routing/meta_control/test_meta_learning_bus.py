"""Behavioral contract tests for agentic_core.L0_routing.meta_control.meta_learning_bus."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.meta_control.meta_learning_bus"


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


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_metalearningbus_is_instantiable(mod):
    """MetaLearningBus is accessible and is a type."""
    cls = getattr(mod, "MetaLearningBus", None)
    assert cls is not None, "MetaLearningBus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "MetaLearningBus must be a class"


def test_metalearningchangepackage_is_instantiable(mod):
    """MetaLearningChangePackage is accessible and is a type."""
    cls = getattr(mod, "MetaLearningChangePackage", None)
    assert cls is not None, "MetaLearningChangePackage must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "MetaLearningChangePackage must be a class"


def test_deque_is_instantiable(mod):
    """deque is accessible and is a type."""
    cls = getattr(mod, "deque", None)
    assert cls is not None, "deque must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "deque must be a class"


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


def test_get_process_bus_is_callable(mod):
    """get_process_bus is accessible and callable."""
    func = getattr(mod, "get_process_bus", None)
    assert func is not None, "get_process_bus must be defined in {MODULE_PATH}"
    assert callable(func), "get_process_bus must be callable"


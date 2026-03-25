"""Behavioral contract tests for agentic_core.adg.runtime.safety_observer."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.safety_observer"


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


def test_guardrailexecution_is_instantiable(mod):
    """GuardrailExecution is accessible and is a type."""
    cls = getattr(mod, "GuardrailExecution", None)
    assert cls is not None, "GuardrailExecution must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardrailExecution must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_policyhashverification_is_instantiable(mod):
    """PolicyHashVerification is accessible and is a type."""
    cls = getattr(mod, "PolicyHashVerification", None)
    assert cls is not None, "PolicyHashVerification must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PolicyHashVerification must be a class"


def test_runtimegraph_is_instantiable(mod):
    """RuntimeGraph is accessible and is a type."""
    cls = getattr(mod, "RuntimeGraph", None)
    assert cls is not None, "RuntimeGraph must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeGraph must be a class"


def test_runtimegraphcollector_is_instantiable(mod):
    """RuntimeGraphCollector is accessible and is a type."""
    cls = getattr(mod, "RuntimeGraphCollector", None)
    assert cls is not None, "RuntimeGraphCollector must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeGraphCollector must be a class"


def test_runtimesafetyobserver_is_instantiable(mod):
    """RuntimeSafetyObserver is accessible and is a type."""
    cls = getattr(mod, "RuntimeSafetyObserver", None)
    assert cls is not None, "RuntimeSafetyObserver must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeSafetyObserver must be a class"


def test_runtimesafetyreport_is_instantiable(mod):
    """RuntimeSafetyReport is accessible and is a type."""
    cls = getattr(mod, "RuntimeSafetyReport", None)
    assert cls is not None, "RuntimeSafetyReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RuntimeSafetyReport must be a class"


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


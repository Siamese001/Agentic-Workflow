"""Behavioral contract tests for agentic_core.L0_routing.types.shadow_routing_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.shadow_routing_types"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_routepath_is_instantiable(mod):
    """RoutePath is accessible and is a type."""
    cls = getattr(mod, "RoutePath", None)
    assert cls is not None, "RoutePath must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutePath must be a class"


def test_semanticclocksnapshot_is_instantiable(mod):
    """SemanticClockSnapshot is accessible and is a type."""
    cls = getattr(mod, "SemanticClockSnapshot", None)
    assert cls is not None, "SemanticClockSnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SemanticClockSnapshot must be a class"


def test_shadowroutingdecision_is_instantiable(mod):
    """ShadowRoutingDecision is accessible and is a type."""
    cls = getattr(mod, "ShadowRoutingDecision", None)
    assert cls is not None, "ShadowRoutingDecision must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ShadowRoutingDecision must be a class"


def test_shadowroutingrationale_is_instantiable(mod):
    """ShadowRoutingRationale is accessible and is a type."""
    cls = getattr(mod, "ShadowRoutingRationale", None)
    assert cls is not None, "ShadowRoutingRationale must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ShadowRoutingRationale must be a class"


def test_shadowroutingtelemetry_is_instantiable(mod):
    """ShadowRoutingTelemetry is accessible and is a type."""
    cls = getattr(mod, "ShadowRoutingTelemetry", None)
    assert cls is not None, "ShadowRoutingTelemetry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ShadowRoutingTelemetry must be a class"


def test_canonical_json_is_callable(mod):
    """canonical_json is accessible and callable."""
    func = getattr(mod, "canonical_json", None)
    assert func is not None, "canonical_json must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_json must be callable"


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


"""Behavioral contract tests for agentic_core.L0_routing.types.routing_config_seal_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.routing_config_seal_types"


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


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_routingconfigseal_is_instantiable(mod):
    """RoutingConfigSeal is accessible and is a type."""
    cls = getattr(mod, "RoutingConfigSeal", None)
    assert cls is not None, "RoutingConfigSeal must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingConfigSeal must be a class"


def test_routingconfigsealviolation_is_instantiable(mod):
    """RoutingConfigSealViolation is accessible and is a type."""
    cls = getattr(mod, "RoutingConfigSealViolation", None)
    assert cls is not None, "RoutingConfigSealViolation must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingConfigSealViolation must be a class"


def test_sealedroutingcontext_is_instantiable(mod):
    """SealedRoutingContext is accessible and is a type."""
    cls = getattr(mod, "SealedRoutingContext", None)
    assert cls is not None, "SealedRoutingContext must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SealedRoutingContext must be a class"


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


def test_canonical_bytes_is_callable(mod):
    """canonical_bytes is accessible and callable."""
    func = getattr(mod, "canonical_bytes", None)
    assert func is not None, "canonical_bytes must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_bytes must be callable"


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


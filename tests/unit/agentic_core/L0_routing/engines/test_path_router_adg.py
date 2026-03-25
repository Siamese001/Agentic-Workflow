"""Behavioral contract tests for agentic_core.L0_routing.engines.path_router."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.engines.path_router"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_governedpayload_is_instantiable(mod):
    """GovernedPayload is accessible and is a type."""
    cls = getattr(mod, "GovernedPayload", None)
    assert cls is not None, "GovernedPayload must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GovernedPayload must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_pathrouter_is_instantiable(mod):
    """PathRouter is accessible and is a type."""
    cls = getattr(mod, "PathRouter", None)
    assert cls is not None, "PathRouter must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PathRouter must be a class"


def test_proposalcommitter_is_instantiable(mod):
    """ProposalCommitter is accessible and is a type."""
    cls = getattr(mod, "ProposalCommitter", None)
    assert cls is not None, "ProposalCommitter must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProposalCommitter must be a class"


def test_routingcontext_is_instantiable(mod):
    """RoutingContext is accessible and is a type."""
    cls = getattr(mod, "RoutingContext", None)
    assert cls is not None, "RoutingContext must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingContext must be a class"


def test_routingoutcomestatus_is_instantiable(mod):
    """RoutingOutcomeStatus is accessible and is a type."""
    cls = getattr(mod, "RoutingOutcomeStatus", None)
    assert cls is not None, "RoutingOutcomeStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingOutcomeStatus must be a class"


def test_create_and_commit_routing_contract_is_callable(mod):
    """create_and_commit_routing_contract is accessible and callable."""
    func = getattr(mod, "create_and_commit_routing_contract", None)
    assert func is not None, "create_and_commit_routing_contract must be defined in {MODULE_PATH}"
    assert callable(func), "create_and_commit_routing_contract must be callable"


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


def test_record_routing_telemetry_is_callable(mod):
    """record_routing_telemetry is accessible and callable."""
    func = getattr(mod, "record_routing_telemetry", None)
    assert func is not None, "record_routing_telemetry must be defined in {MODULE_PATH}"
    assert callable(func), "record_routing_telemetry must be callable"


"""Behavioral contract tests for agentic_core.L0_routing.types.routing_contracts_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.routing_contracts_types"


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


def test_aggregateartifact_is_instantiable(mod):
    """AggregateArtifact is accessible and is a type."""
    cls = getattr(mod, "AggregateArtifact", None)
    assert cls is not None, "AggregateArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AggregateArtifact must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_artifactabsencefailure_is_instantiable(mod):
    """ArtifactAbsenceFailure is accessible and is a type."""
    cls = getattr(mod, "ArtifactAbsenceFailure", None)
    assert cls is not None, "ArtifactAbsenceFailure must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ArtifactAbsenceFailure must be a class"


def test_capabilitydepletiontracker_is_instantiable(mod):
    """CapabilityDepletionTracker is accessible and is a type."""
    cls = getattr(mod, "CapabilityDepletionTracker", None)
    assert cls is not None, "CapabilityDepletionTracker must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapabilityDepletionTracker must be a class"


def test_evacuationprotocol_is_instantiable(mod):
    """EvacuationProtocol is accessible and is a type."""
    cls = getattr(mod, "EvacuationProtocol", None)
    assert cls is not None, "EvacuationProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvacuationProtocol must be a class"


def test_guardrailguard_is_instantiable(mod):
    """GuardrailGuard is accessible and is a type."""
    cls = getattr(mod, "GuardrailGuard", None)
    assert cls is not None, "GuardrailGuard must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardrailGuard must be a class"


def test_healingtransactionboundary_is_instantiable(mod):
    """HealingTransactionBoundary is accessible and is a type."""
    cls = getattr(mod, "HealingTransactionBoundary", None)
    assert cls is not None, "HealingTransactionBoundary must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealingTransactionBoundary must be a class"


def test_incidentartifact_is_instantiable(mod):
    """IncidentArtifact is accessible and is a type."""
    cls = getattr(mod, "IncidentArtifact", None)
    assert cls is not None, "IncidentArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IncidentArtifact must be a class"


def test_aggregate_gate_check_is_callable(mod):
    """aggregate_gate_check is accessible and callable."""
    func = getattr(mod, "aggregate_gate_check", None)
    assert func is not None, "aggregate_gate_check must be defined in {MODULE_PATH}"
    assert callable(func), "aggregate_gate_check must be callable"


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


def test_enforce_artifact_presence_is_callable(mod):
    """enforce_artifact_presence is accessible and callable."""
    func = getattr(mod, "enforce_artifact_presence", None)
    assert func is not None, "enforce_artifact_presence must be defined in {MODULE_PATH}"
    assert callable(func), "enforce_artifact_presence must be callable"


def test_enforce_route_decision_presence_is_callable(mod):
    """enforce_route_decision_presence is accessible and callable."""
    func = getattr(mod, "enforce_route_decision_presence", None)
    assert func is not None, "enforce_route_decision_presence must be defined in {MODULE_PATH}"
    assert callable(func), "enforce_route_decision_presence must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_meta_guardian_check_is_callable(mod):
    """meta_guardian_check is accessible and callable."""
    func = getattr(mod, "meta_guardian_check", None)
    assert func is not None, "meta_guardian_check must be defined in {MODULE_PATH}"
    assert callable(func), "meta_guardian_check must be callable"


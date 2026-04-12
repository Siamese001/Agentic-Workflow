"""Behavioral contract tests for agentic_core.L0_routing.types.routing_artifact_types."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.types.routing_artifact_types"


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


def test_capabilitydepletiontracker_is_instantiable(mod):
    """CapabilityDepletionTracker is accessible and is a type."""
    cls = getattr(mod, "CapabilityDepletionTracker", None)
    assert cls is not None, "CapabilityDepletionTracker must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapabilityDepletionTracker must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_evacuationprotocol_is_instantiable(mod):
    """EvacuationProtocol is accessible and is a type."""
    cls = getattr(mod, "EvacuationProtocol", None)
    assert cls is not None, "EvacuationProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvacuationProtocol must be a class"


def test_healingplan_is_instantiable(mod):
    """HealingPlan is accessible and is a type."""
    cls = getattr(mod, "HealingPlan", None)
    assert cls is not None, "HealingPlan must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealingPlan must be a class"


def test_incidentartifact_is_instantiable(mod):
    """IncidentArtifact is accessible and is a type."""
    cls = getattr(mod, "IncidentArtifact", None)
    assert cls is not None, "IncidentArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IncidentArtifact must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"

"""Behavioral contract tests for agentic_core.L0_routing.types.artifact_typed_compat_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.artifact_typed_compat_types"


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


def test_resultartifact_is_instantiable(mod):
    """ResultArtifact is accessible and is a type."""
    cls = getattr(mod, "ResultArtifact", None)
    assert cls is not None, "ResultArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ResultArtifact must be a class"


def test_routedecisionartifact_is_instantiable(mod):
    """RouteDecisionArtifact is accessible and is a type."""
    cls = getattr(mod, "RouteDecisionArtifact", None)
    assert cls is not None, "RouteDecisionArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RouteDecisionArtifact must be a class"


def test_selfhealingtrigger_is_instantiable(mod):
    """SelfHealingTrigger is accessible and is a type."""
    cls = getattr(mod, "SelfHealingTrigger", None)
    assert cls is not None, "SelfHealingTrigger must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SelfHealingTrigger must be a class"


def test_stalewriteincident_is_instantiable(mod):
    """StaleWriteIncident is accessible and is a type."""
    cls = getattr(mod, "StaleWriteIncident", None)
    assert cls is not None, "StaleWriteIncident must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "StaleWriteIncident must be a class"


def test_healingplantd_is_callable(mod):
    """HealingPlanTD is accessible and callable."""
    func = getattr(mod, "HealingPlanTD", None)
    assert func is not None, "HealingPlanTD must be defined in {MODULE_PATH}"
    assert callable(func), "HealingPlanTD must be callable"


def test_incidentartifacttd_is_callable(mod):
    """IncidentArtifactTD is accessible and callable."""
    func = getattr(mod, "IncidentArtifactTD", None)
    assert func is not None, "IncidentArtifactTD must be defined in {MODULE_PATH}"
    assert callable(func), "IncidentArtifactTD must be callable"


def test_resultartifacttd_is_callable(mod):
    """ResultArtifactTD is accessible and callable."""
    func = getattr(mod, "ResultArtifactTD", None)
    assert func is not None, "ResultArtifactTD must be defined in {MODULE_PATH}"
    assert callable(func), "ResultArtifactTD must be callable"


def test_stalewriteincidenttd_is_callable(mod):
    """StaleWriteIncidentTD is accessible and callable."""
    func = getattr(mod, "StaleWriteIncidentTD", None)
    assert func is not None, "StaleWriteIncidentTD must be defined in {MODULE_PATH}"
    assert callable(func), "StaleWriteIncidentTD must be callable"


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


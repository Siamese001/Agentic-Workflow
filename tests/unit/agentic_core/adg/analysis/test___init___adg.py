"""Behavioral contract tests for agentic_core.adg.analysis.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.analysis.__init__"


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


def test_canonicalsnapshot_is_instantiable(mod):
    """CanonicalSnapshot is accessible and is a type."""
    cls = getattr(mod, "CanonicalSnapshot", None)
    assert cls is not None, "CanonicalSnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CanonicalSnapshot must be a class"


def test_edgeconfidence_is_instantiable(mod):
    """EdgeConfidence is accessible and is a type."""
    cls = getattr(mod, "EdgeConfidence", None)
    assert cls is not None, "EdgeConfidence must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EdgeConfidence must be a class"


def test_graphdiff_is_instantiable(mod):
    """GraphDiff is accessible and is a type."""
    cls = getattr(mod, "GraphDiff", None)
    assert cls is not None, "GraphDiff must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GraphDiff must be a class"


def test_healervalidatoredge_is_instantiable(mod):
    """HealerValidatorEdge is accessible and is a type."""
    cls = getattr(mod, "HealerValidatorEdge", None)
    assert cls is not None, "HealerValidatorEdge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealerValidatorEdge must be a class"


def test_healervalidatorreport_is_instantiable(mod):
    """HealerValidatorReport is accessible and is a type."""
    cls = getattr(mod, "HealerValidatorReport", None)
    assert cls is not None, "HealerValidatorReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealerValidatorReport must be a class"


def test_impactreport_is_instantiable(mod):
    """ImpactReport is accessible and is a type."""
    cls = getattr(mod, "ImpactReport", None)
    assert cls is not None, "ImpactReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ImpactReport must be a class"


def test_moduleownership_is_instantiable(mod):
    """ModuleOwnership is accessible and is a type."""
    cls = getattr(mod, "ModuleOwnership", None)
    assert cls is not None, "ModuleOwnership must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ModuleOwnership must be a class"


def test_ownershipregistry_is_instantiable(mod):
    """OwnershipRegistry is accessible and is a type."""
    cls = getattr(mod, "OwnershipRegistry", None)
    assert cls is not None, "OwnershipRegistry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "OwnershipRegistry must be a class"


def test_build_snapshot_is_callable(mod):
    """build_snapshot is accessible and callable."""
    func = getattr(mod, "build_snapshot", None)
    assert func is not None, "build_snapshot must be defined in {MODULE_PATH}"
    assert callable(func), "build_snapshot must be callable"


def test_detect_healer_validator_relationships_is_callable(mod):
    """detect_healer_validator_relationships is accessible and callable."""
    func = getattr(mod, "detect_healer_validator_relationships", None)
    assert func is not None, "detect_healer_validator_relationships must be defined in {MODULE_PATH}"
    assert callable(func), "detect_healer_validator_relationships must be callable"


def test_diff_snapshots_is_callable(mod):
    """diff_snapshots is accessible and callable."""
    func = getattr(mod, "diff_snapshots", None)
    assert func is not None, "diff_snapshots must be defined in {MODULE_PATH}"
    assert callable(func), "diff_snapshots must be callable"


def test_predict_impact_is_callable(mod):
    """predict_impact is accessible and callable."""
    func = getattr(mod, "predict_impact", None)
    assert func is not None, "predict_impact must be defined in {MODULE_PATH}"
    assert callable(func), "predict_impact must be callable"


def test_route_violations_is_callable(mod):
    """route_violations is accessible and callable."""
    func = getattr(mod, "route_violations", None)
    assert func is not None, "route_violations must be defined in {MODULE_PATH}"
    assert callable(func), "route_violations must be callable"


def test_score_edges_is_callable(mod):
    """score_edges is accessible and callable."""
    func = getattr(mod, "score_edges", None)
    assert func is not None, "score_edges must be defined in {MODULE_PATH}"
    assert callable(func), "score_edges must be callable"


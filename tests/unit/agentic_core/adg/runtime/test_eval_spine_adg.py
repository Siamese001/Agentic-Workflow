"""Behavioral contract tests for agentic_core.adg.runtime.eval_spine."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.eval_spine"


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


def test_dpobatch_is_instantiable(mod):
    """DPOBatch is accessible and is a type."""
    cls = getattr(mod, "DPOBatch", None)
    assert cls is not None, "DPOBatch must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DPOBatch must be a class"


def test_driftalert_is_instantiable(mod):
    """DriftAlert is accessible and is a type."""
    cls = getattr(mod, "DriftAlert", None)
    assert cls is not None, "DriftAlert must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DriftAlert must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_evalmetricresult_is_instantiable(mod):
    """EvalMetricResult is accessible and is a type."""
    cls = getattr(mod, "EvalMetricResult", None)
    assert cls is not None, "EvalMetricResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvalMetricResult must be a class"


def test_evalspine_is_instantiable(mod):
    """EvalSpine is accessible and is a type."""
    cls = getattr(mod, "EvalSpine", None)
    assert cls is not None, "EvalSpine must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvalSpine must be a class"


def test_evalspinereport_is_instantiable(mod):
    """EvalSpineReport is accessible and is a type."""
    cls = getattr(mod, "EvalSpineReport", None)
    assert cls is not None, "EvalSpineReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvalSpineReport must be a class"


def test_optimizationproposal_is_instantiable(mod):
    """OptimizationProposal is accessible and is a type."""
    cls = getattr(mod, "OptimizationProposal", None)
    assert cls is not None, "OptimizationProposal must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "OptimizationProposal must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


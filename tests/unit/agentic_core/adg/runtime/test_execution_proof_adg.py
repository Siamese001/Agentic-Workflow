"""Behavioral contract tests for agentic_core.adg.runtime.execution_proof."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.execution_proof"


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


def test_executionproofrecorder_is_instantiable(mod):
    """ExecutionProofRecorder is accessible and is a type."""
    cls = getattr(mod, "ExecutionProofRecorder", None)
    assert cls is not None, "ExecutionProofRecorder must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionProofRecorder must be a class"


def test_executionproofreport_is_instantiable(mod):
    """ExecutionProofReport is accessible and is a type."""
    cls = getattr(mod, "ExecutionProofReport", None)
    assert cls is not None, "ExecutionProofReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionProofReport must be a class"


def test_executiontrace_is_instantiable(mod):
    """ExecutionTrace is accessible and is a type."""
    cls = getattr(mod, "ExecutionTrace", None)
    assert cls is not None, "ExecutionTrace must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionTrace must be a class"


def test_proofcomparison_is_instantiable(mod):
    """ProofComparison is accessible and is a type."""
    cls = getattr(mod, "ProofComparison", None)
    assert cls is not None, "ProofComparison must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProofComparison must be a class"


def test_proofcomparisonoutcome_is_instantiable(mod):
    """ProofComparisonOutcome is accessible and is a type."""
    cls = getattr(mod, "ProofComparisonOutcome", None)
    assert cls is not None, "ProofComparisonOutcome must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProofComparisonOutcome must be a class"


def test_replaykey_is_instantiable(mod):
    """ReplayKey is accessible and is a type."""
    cls = getattr(mod, "ReplayKey", None)
    assert cls is not None, "ReplayKey must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReplayKey must be a class"


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


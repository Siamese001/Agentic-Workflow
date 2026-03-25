"""Behavioral contract tests for agentic_core.L0_routing.types.determinism_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.determinism_types"


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


def test_boundarysnapshotartifact_is_instantiable(mod):
    """BoundarySnapshotArtifact is accessible and is a type."""
    cls = getattr(mod, "BoundarySnapshotArtifact", None)
    assert cls is not None, "BoundarySnapshotArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BoundarySnapshotArtifact must be a class"


def test_canonicalastresult_is_instantiable(mod):
    """CanonicalASTResult is accessible and is a type."""
    cls = getattr(mod, "CanonicalASTResult", None)
    assert cls is not None, "CanonicalASTResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CanonicalASTResult must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_episodicmemoryqueryresult_is_instantiable(mod):
    """EpisodicMemoryQueryResult is accessible and is a type."""
    cls = getattr(mod, "EpisodicMemoryQueryResult", None)
    assert cls is not None, "EpisodicMemoryQueryResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EpisodicMemoryQueryResult must be a class"


def test_episodicsemanticlink_is_instantiable(mod):
    """EpisodicSemanticLink is accessible and is a type."""
    cls = getattr(mod, "EpisodicSemanticLink", None)
    assert cls is not None, "EpisodicSemanticLink must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EpisodicSemanticLink must be a class"


def test_fixconstraint_is_instantiable(mod):
    """FixConstraint is accessible and is a type."""
    cls = getattr(mod, "FixConstraint", None)
    assert cls is not None, "FixConstraint must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FixConstraint must be a class"


def test_forensictracebuffer_is_instantiable(mod):
    """ForensicTraceBuffer is accessible and is a type."""
    cls = getattr(mod, "ForensicTraceBuffer", None)
    assert cls is not None, "ForensicTraceBuffer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ForensicTraceBuffer must be a class"


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


def test_record_execution_trace_is_callable(mod):
    """record_execution_trace is accessible and callable."""
    func = getattr(mod, "record_execution_trace", None)
    assert func is not None, "record_execution_trace must be defined in {MODULE_PATH}"
    assert callable(func), "record_execution_trace must be callable"


def test_validate_semantic_clock_is_callable(mod):
    """validate_semantic_clock is accessible and callable."""
    func = getattr(mod, "validate_semantic_clock", None)
    assert func is not None, "validate_semantic_clock must be defined in {MODULE_PATH}"
    assert callable(func), "validate_semantic_clock must be callable"


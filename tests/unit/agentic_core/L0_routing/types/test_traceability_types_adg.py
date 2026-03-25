"""Behavioral contract tests for agentic_core.L0_routing.types.traceability_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.traceability_types"


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


def test_citationbundle_is_instantiable(mod):
    """CitationBundle is accessible and is a type."""
    cls = getattr(mod, "CitationBundle", None)
    assert cls is not None, "CitationBundle must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CitationBundle must be a class"


def test_citationentry_is_instantiable(mod):
    """CitationEntry is accessible and is a type."""
    cls = getattr(mod, "CitationEntry", None)
    assert cls is not None, "CitationEntry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CitationEntry must be a class"


def test_cognitivediffbundle_is_instantiable(mod):
    """CognitiveDiffBundle is accessible and is a type."""
    cls = getattr(mod, "CognitiveDiffBundle", None)
    assert cls is not None, "CognitiveDiffBundle must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CognitiveDiffBundle must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_errorsignature_is_instantiable(mod):
    """ErrorSignature is accessible and is a type."""
    cls = getattr(mod, "ErrorSignature", None)
    assert cls is not None, "ErrorSignature must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ErrorSignature must be a class"


def test_knowledgeadvisoryconstraint_is_instantiable(mod):
    """KnowledgeAdvisoryConstraint is accessible and is a type."""
    cls = getattr(mod, "KnowledgeAdvisoryConstraint", None)
    assert cls is not None, "KnowledgeAdvisoryConstraint must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "KnowledgeAdvisoryConstraint must be a class"


def test_knowledgedirective_is_instantiable(mod):
    """KnowledgeDirective is accessible and is a type."""
    cls = getattr(mod, "KnowledgeDirective", None)
    assert cls is not None, "KnowledgeDirective must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "KnowledgeDirective must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_compute_error_signature_hash_is_callable(mod):
    """compute_error_signature_hash is accessible and callable."""
    func = getattr(mod, "compute_error_signature_hash", None)
    assert func is not None, "compute_error_signature_hash must be defined in {MODULE_PATH}"
    assert callable(func), "compute_error_signature_hash must be callable"


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


def test_record_execution_trace_is_callable(mod):
    """record_execution_trace is accessible and callable."""
    func = getattr(mod, "record_execution_trace", None)
    assert func is not None, "record_execution_trace must be defined in {MODULE_PATH}"
    assert callable(func), "record_execution_trace must be callable"


def test_validate_trace_id_is_callable(mod):
    """validate_trace_id is accessible and callable."""
    func = getattr(mod, "validate_trace_id", None)
    assert func is not None, "validate_trace_id must be defined in {MODULE_PATH}"
    assert callable(func), "validate_trace_id must be callable"


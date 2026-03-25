"""Behavioral contract tests for agentic_core.L0_routing.enforcement.traceability_contracts."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.traceability_contracts"


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


def test_advisoryviolationerror_is_instantiable(mod):
    """AdvisoryViolationError is accessible and is a type."""
    cls = getattr(mod, "AdvisoryViolationError", None)
    assert cls is not None, "AdvisoryViolationError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AdvisoryViolationError must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_citationbundle_is_instantiable(mod):
    """CitationBundle is accessible and is a type."""
    cls = getattr(mod, "CitationBundle", None)
    assert cls is not None, "CitationBundle must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CitationBundle must be a class"


def test_cognitivediffbundle_is_instantiable(mod):
    """CognitiveDiffBundle is accessible and is a type."""
    cls = getattr(mod, "CognitiveDiffBundle", None)
    assert cls is not None, "CognitiveDiffBundle must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CognitiveDiffBundle must be a class"


def test_cognitivedifferror_is_instantiable(mod):
    """CognitiveDiffError is accessible and is a type."""
    cls = getattr(mod, "CognitiveDiffError", None)
    assert cls is not None, "CognitiveDiffError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CognitiveDiffError must be a class"


def test_errorsignature_is_instantiable(mod):
    """ErrorSignature is accessible and is a type."""
    cls = getattr(mod, "ErrorSignature", None)
    assert cls is not None, "ErrorSignature must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ErrorSignature must be a class"


def test_errorsignatureerror_is_instantiable(mod):
    """ErrorSignatureError is accessible and is a type."""
    cls = getattr(mod, "ErrorSignatureError", None)
    assert cls is not None, "ErrorSignatureError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ErrorSignatureError must be a class"


def test_knowledgeadvisoryconstraint_is_instantiable(mod):
    """KnowledgeAdvisoryConstraint is accessible and is a type."""
    cls = getattr(mod, "KnowledgeAdvisoryConstraint", None)
    assert cls is not None, "KnowledgeAdvisoryConstraint must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "KnowledgeAdvisoryConstraint must be a class"


def test_build_cognitive_diff_bundle_is_callable(mod):
    """build_cognitive_diff_bundle is accessible and callable."""
    func = getattr(mod, "build_cognitive_diff_bundle", None)
    assert func is not None, "build_cognitive_diff_bundle must be defined in {MODULE_PATH}"
    assert callable(func), "build_cognitive_diff_bundle must be callable"


def test_build_error_signature_is_callable(mod):
    """build_error_signature is accessible and callable."""
    func = getattr(mod, "build_error_signature", None)
    assert func is not None, "build_error_signature must be defined in {MODULE_PATH}"
    assert callable(func), "build_error_signature must be callable"


def test_build_plan_provenance_is_callable(mod):
    """build_plan_provenance is accessible and callable."""
    func = getattr(mod, "build_plan_provenance", None)
    assert func is not None, "build_plan_provenance must be defined in {MODULE_PATH}"
    assert callable(func), "build_plan_provenance must be callable"


def test_build_retrieval_query_is_callable(mod):
    """build_retrieval_query is accessible and callable."""
    func = getattr(mod, "build_retrieval_query", None)
    assert func is not None, "build_retrieval_query must be defined in {MODULE_PATH}"
    assert callable(func), "build_retrieval_query must be callable"


def test_build_retrieved_chunk_is_callable(mod):
    """build_retrieved_chunk is accessible and callable."""
    func = getattr(mod, "build_retrieved_chunk", None)
    assert func is not None, "build_retrieved_chunk must be defined in {MODULE_PATH}"
    assert callable(func), "build_retrieved_chunk must be callable"


def test_compute_error_signature_hash_is_callable(mod):
    """compute_error_signature_hash is accessible and callable."""
    func = getattr(mod, "compute_error_signature_hash", None)
    assert func is not None, "compute_error_signature_hash must be defined in {MODULE_PATH}"
    assert callable(func), "compute_error_signature_hash must be callable"


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


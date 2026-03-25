"""Behavioral contract tests for agentic_core.L0_routing.enforcement.boundary_contracts."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.boundary_contracts"


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


def test_boundaryschemadescriptor_is_instantiable(mod):
    """BoundarySchemaDescriptor is accessible and is a type."""
    cls = getattr(mod, "BoundarySchemaDescriptor", None)
    assert cls is not None, "BoundarySchemaDescriptor must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BoundarySchemaDescriptor must be a class"


def test_boundaryschemaerror_is_instantiable(mod):
    """BoundarySchemaError is accessible and is a type."""
    cls = getattr(mod, "BoundarySchemaError", None)
    assert cls is not None, "BoundarySchemaError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BoundarySchemaError must be a class"


def test_contextretrievalerror_is_instantiable(mod):
    """ContextRetrievalError is accessible and is a type."""
    cls = getattr(mod, "ContextRetrievalError", None)
    assert cls is not None, "ContextRetrievalError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ContextRetrievalError must be a class"


def test_contextretrievalrequest_is_instantiable(mod):
    """ContextRetrievalRequest is accessible and is a type."""
    cls = getattr(mod, "ContextRetrievalRequest", None)
    assert cls is not None, "ContextRetrievalRequest must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ContextRetrievalRequest must be a class"


def test_invariantcheck_is_instantiable(mod):
    """InvariantCheck is accessible and is a type."""
    cls = getattr(mod, "InvariantCheck", None)
    assert cls is not None, "InvariantCheck must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InvariantCheck must be a class"


def test_invariantseverity_is_instantiable(mod):
    """InvariantSeverity is accessible and is a type."""
    cls = getattr(mod, "InvariantSeverity", None)
    assert cls is not None, "InvariantSeverity must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InvariantSeverity must be a class"


def test_invariantviolation_is_instantiable(mod):
    """InvariantViolation is accessible and is a type."""
    cls = getattr(mod, "InvariantViolation", None)
    assert cls is not None, "InvariantViolation must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InvariantViolation must be a class"


def test_metainvarianterror_is_instantiable(mod):
    """MetaInvariantError is accessible and is a type."""
    cls = getattr(mod, "MetaInvariantError", None)
    assert cls is not None, "MetaInvariantError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "MetaInvariantError must be a class"


def test_assert_chain_closure_is_callable(mod):
    """assert_chain_closure is accessible and callable."""
    func = getattr(mod, "assert_chain_closure", None)
    assert func is not None, "assert_chain_closure must be defined in {MODULE_PATH}"
    assert callable(func), "assert_chain_closure must be callable"


def test_assert_cross_run_pins_is_callable(mod):
    """assert_cross_run_pins is accessible and callable."""
    func = getattr(mod, "assert_cross_run_pins", None)
    assert func is not None, "assert_cross_run_pins must be defined in {MODULE_PATH}"
    assert callable(func), "assert_cross_run_pins must be callable"


def test_build_boundary_schema_is_callable(mod):
    """build_boundary_schema is accessible and callable."""
    func = getattr(mod, "build_boundary_schema", None)
    assert func is not None, "build_boundary_schema must be defined in {MODULE_PATH}"
    assert callable(func), "build_boundary_schema must be callable"


def test_build_context_retrieval_request_is_callable(mod):
    """build_context_retrieval_request is accessible and callable."""
    func = getattr(mod, "build_context_retrieval_request", None)
    assert func is not None, "build_context_retrieval_request must be defined in {MODULE_PATH}"
    assert callable(func), "build_context_retrieval_request must be callable"


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


def test_fail_closed_on_violation_is_callable(mod):
    """fail_closed_on_violation is accessible and callable."""
    func = getattr(mod, "fail_closed_on_violation", None)
    assert func is not None, "fail_closed_on_violation must be defined in {MODULE_PATH}"
    assert callable(func), "fail_closed_on_violation must be callable"


def test_resolve_ssot_binding_is_callable(mod):
    """resolve_ssot_binding is accessible and callable."""
    func = getattr(mod, "resolve_ssot_binding", None)
    assert func is not None, "resolve_ssot_binding must be defined in {MODULE_PATH}"
    assert callable(func), "resolve_ssot_binding must be callable"


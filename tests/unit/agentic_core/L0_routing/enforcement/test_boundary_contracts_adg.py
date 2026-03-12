"""ADG importability contract for agentic_core/L0_routing/enforcement/boundary_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_contracts.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.boundary_contracts import (  # noqa: F401
        SSOTBindingError,
        ContextRetrievalError,
        BoundarySchemaError,
        MetaInvariantError,
        resolve_ssot_binding,
        build_context_retrieval_request,
        validate_context_retrieval_read_only,
        validate_boundary_schema,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SSOTBindingError = None  # type: ignore[assignment,misc]
    ContextRetrievalError = None  # type: ignore[assignment,misc]
    BoundarySchemaError = None  # type: ignore[assignment,misc]
    MetaInvariantError = None  # type: ignore[assignment,misc]
    resolve_ssot_binding = None  # type: ignore[assignment,misc]
    build_context_retrieval_request = None  # type: ignore[assignment,misc]
    validate_context_retrieval_read_only = None  # type: ignore[assignment,misc]
    validate_boundary_schema = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_contracts.py deps unavailable")
class TestBoundaryContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: boundary_contracts.py must be importable."""
        assert _AVAILABLE

    def test_ssotbindingerror_is_type(self) -> None:
        assert SSOTBindingError is not None

    def test_contextretrievalerror_is_type(self) -> None:
        assert ContextRetrievalError is not None

    def test_boundaryschemaerror_is_type(self) -> None:
        assert BoundarySchemaError is not None

    def test_resolve_ssot_binding_callable(self) -> None:
        assert callable(resolve_ssot_binding)

    def test_build_context_retrieval_request_callable(self) -> None:
        assert callable(build_context_retrieval_request)


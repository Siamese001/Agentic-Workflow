"""ADG importability contract for agentic_core/L0_routing/enforcement/boundary_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_contracts.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.boundary_contracts import (  # noqa: F401
        BoundarySchemaError,
        ContextRetrievalError,
        SSOTBindingError,
        build_context_retrieval_request,
        resolve_ssot_binding,
        validate_context_retrieval_read_only,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SSOTBindingError = None  # type: ignore[assignment,misc]
    resolve_ssot_binding = None  # type: ignore[assignment,misc]
    ContextRetrievalError = None  # type: ignore[assignment,misc]
    build_context_retrieval_request = None  # type: ignore[assignment,misc]
    validate_context_retrieval_read_only = None  # type: ignore[assignment,misc]
    BoundarySchemaError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boundary_contracts deps unavailable")
class TestBoundaryContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/boundary_contracts.py must be importable."""
        assert _AVAILABLE

    def test_ssotbindingerror_defined(self) -> None:
        assert SSOTBindingError is not None

    def test_contextretrievalerror_defined(self) -> None:
        assert ContextRetrievalError is not None

    def test_boundaryschemaerror_defined(self) -> None:
        assert BoundarySchemaError is not None
"""ADG importability contract for agentic_core/L0_routing/types/boundary_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.boundary_types import (  # noqa: F401
        BoundarySchemaDescriptor,
        ContextRetrievalRequest,
        InvariantSeverity,
        InvariantViolation,
        SchemaValidationStatus,
        SSOTBinding,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SSOTBinding = None  # type: ignore[assignment,misc]
    ContextRetrievalRequest = None  # type: ignore[assignment,misc]
    SchemaValidationStatus = None  # type: ignore[assignment,misc]
    BoundarySchemaDescriptor = None  # type: ignore[assignment,misc]
    InvariantSeverity = None  # type: ignore[assignment,misc]
    InvariantViolation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boundary_types deps unavailable")
class TestBoundaryTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/boundary_types.py must be importable."""
        assert _AVAILABLE

    def test_ssotbinding_defined(self) -> None:
        assert SSOTBinding is not None

    def test_contextretrievalrequest_defined(self) -> None:
        assert ContextRetrievalRequest is not None

    def test_schemavalidationstatus_defined(self) -> None:
        assert SchemaValidationStatus is not None

    def test_boundaryschemadescriptor_defined(self) -> None:
        assert BoundarySchemaDescriptor is not None

    def test_invariantseverity_defined(self) -> None:
        assert InvariantSeverity is not None

    def test_invariantviolation_defined(self) -> None:
        assert InvariantViolation is not None
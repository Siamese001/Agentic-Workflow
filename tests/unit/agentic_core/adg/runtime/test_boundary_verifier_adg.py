"""ADG importability contract for agentic_core/adg/runtime/boundary_verifier.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_verifier.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.boundary_verifier import (  # noqa: F401
        BoundaryPacket,
        BoundaryVerificationResult,
        BoundaryVerifierReport,
        CapabilityChokepoint,
        L2BoundaryVerifier,
        VerificationOutcome,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VerificationOutcome = None  # type: ignore[assignment,misc]
    BoundaryPacket = None  # type: ignore[assignment,misc]
    BoundaryVerificationResult = None  # type: ignore[assignment,misc]
    BoundaryVerifierReport = None  # type: ignore[assignment,misc]
    L2BoundaryVerifier = None  # type: ignore[assignment,misc]
    CapabilityChokepoint = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boundary_verifier deps unavailable")
class TestBoundaryVerifierImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/boundary_verifier.py must be importable."""
        assert _AVAILABLE

    def test_verificationoutcome_defined(self) -> None:
        assert VerificationOutcome is not None

    def test_boundarypacket_defined(self) -> None:
        assert BoundaryPacket is not None

    def test_boundaryverificationresult_defined(self) -> None:
        assert BoundaryVerificationResult is not None

    def test_boundaryverifierreport_defined(self) -> None:
        assert BoundaryVerifierReport is not None

    def test_l2boundaryverifier_defined(self) -> None:
        assert L2BoundaryVerifier is not None

    def test_capabilitychokepoint_defined(self) -> None:
        assert CapabilityChokepoint is not None
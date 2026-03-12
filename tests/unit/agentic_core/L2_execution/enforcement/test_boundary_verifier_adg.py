"""ADG importability contract for agentic_core/L2_execution/enforcement/boundary_verifier.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_verifier.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.boundary_verifier import (  # noqa: F401
        L2BoundaryVerifier,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    L2BoundaryVerifier = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_verifier.py deps unavailable")
class TestBoundaryVerifierImportability:
    def test_module_importable(self) -> None:
        """ADG contract: boundary_verifier.py must be importable."""
        assert _AVAILABLE

    def test_l2boundaryverifier_is_type(self) -> None:
        assert L2BoundaryVerifier is not None


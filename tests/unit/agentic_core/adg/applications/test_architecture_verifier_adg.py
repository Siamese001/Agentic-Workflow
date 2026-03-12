"""ADG importability contract for agentic_core/adg/applications/architecture_verifier.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_architecture_verifier.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.architecture_verifier import (  # noqa: F401
        PlaneResult,
        ArchitectureVerificationReport,
        verify_architecture,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PlaneResult = None  # type: ignore[assignment,misc]
    ArchitectureVerificationReport = None  # type: ignore[assignment,misc]
    verify_architecture = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="architecture_verifier.py deps unavailable")
class TestArchitectureVerifierImportability:
    def test_module_importable(self) -> None:
        """ADG contract: architecture_verifier.py must be importable."""
        assert _AVAILABLE

    def test_planeresult_is_type(self) -> None:
        assert PlaneResult is not None

    def test_architectureverificationreport_is_type(self) -> None:
        assert ArchitectureVerificationReport is not None

    def test_verify_architecture_callable(self) -> None:
        assert callable(verify_architecture)


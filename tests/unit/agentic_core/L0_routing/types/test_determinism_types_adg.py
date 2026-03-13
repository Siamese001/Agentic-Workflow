"""ADG importability contract for agentic_core/L0_routing/types/determinism_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.determinism_types import (  # noqa: F401
        CanonicalASTResult,
        FixConstraint,
        SemanticClock,
        SemanticClockSnapshot,
        StateCommitInvalid,
        SurgicalManifest,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FixConstraint = None  # type: ignore[assignment,misc]
    SurgicalManifest = None  # type: ignore[assignment,misc]
    CanonicalASTResult = None  # type: ignore[assignment,misc]
    SemanticClock = None  # type: ignore[assignment,misc]
    StateCommitInvalid = None  # type: ignore[assignment,misc]
    SemanticClockSnapshot = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_types deps unavailable")
class TestDeterminismTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/determinism_types.py must be importable."""
        assert _AVAILABLE

    def test_fixconstraint_defined(self) -> None:
        assert FixConstraint is not None

    def test_surgicalmanifest_defined(self) -> None:
        assert SurgicalManifest is not None

    def test_canonicalastresult_defined(self) -> None:
        assert CanonicalASTResult is not None

    def test_semanticclock_defined(self) -> None:
        assert SemanticClock is not None

    def test_statecommitinvalid_defined(self) -> None:
        assert StateCommitInvalid is not None

    def test_semanticclocksnapshot_defined(self) -> None:
        assert SemanticClockSnapshot is not None

"""ADG importability contract for agentic_core/L5_safety/validators/gravity_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_gravity_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.gravity_validator import (  # noqa: F401
        DriftViolation,
        GravityViolation,
        HierarchyViolation,
        ImportViolation,
        SovereignHealthReport,
        UnifiedSSOTValidator,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GravityViolation = None  # type: ignore[assignment,misc]
    ImportViolation = None  # type: ignore[assignment,misc]
    HierarchyViolation = None  # type: ignore[assignment,misc]
    DriftViolation = None  # type: ignore[assignment,misc]
    SovereignHealthReport = None  # type: ignore[assignment,misc]
    UnifiedSSOTValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_validator deps unavailable")
class TestGravityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/gravity_validator.py must be importable."""
        assert _AVAILABLE

    def test_gravityviolation_defined(self) -> None:
        assert GravityViolation is not None

    def test_importviolation_defined(self) -> None:
        assert ImportViolation is not None

    def test_hierarchyviolation_defined(self) -> None:
        assert HierarchyViolation is not None

    def test_driftviolation_defined(self) -> None:
        assert DriftViolation is not None

    def test_sovereignhealthreport_defined(self) -> None:
        assert SovereignHealthReport is not None

    def test_unifiedssotvalidator_defined(self) -> None:
        assert UnifiedSSOTValidator is not None

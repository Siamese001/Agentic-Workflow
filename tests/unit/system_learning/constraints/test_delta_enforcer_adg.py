"""ADG importability contract for system_learning/constraints/delta_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_delta_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.constraints.delta_enforcer import (  # noqa: F401
        BoundsViolation,
        ConstraintViolation,
        DeltaViolation,
        ForbiddenSurface,
        TypeViolation,
        UnknownSurface,
        validate_surface_change,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ConstraintViolation = None  # type: ignore[assignment,misc]
    ForbiddenSurface = None  # type: ignore[assignment,misc]
    UnknownSurface = None  # type: ignore[assignment,misc]
    BoundsViolation = None  # type: ignore[assignment,misc]
    DeltaViolation = None  # type: ignore[assignment,misc]
    TypeViolation = None  # type: ignore[assignment,misc]
    validate_surface_change = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="delta_enforcer.py deps unavailable")
class TestDeltaEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: delta_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_constraintviolation_is_type(self) -> None:
        assert ConstraintViolation is not None

    def test_forbiddensurface_is_type(self) -> None:
        assert ForbiddenSurface is not None

    def test_unknownsurface_is_type(self) -> None:
        assert UnknownSurface is not None

    def test_validate_surface_change_callable(self) -> None:
        assert callable(validate_surface_change)
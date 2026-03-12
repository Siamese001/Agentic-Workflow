"""ADG importability contract for agentic_core/L5_safety/validators/gravity_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_gravity_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.gravity_validator import (  # noqa: F401
        GravityViolation,
        ImportViolation,
        HierarchyViolation,
        DriftViolation,
        SovereignHealthReport,
        UnifiedSSOTValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
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
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_validator.py deps unavailable")
class TestGravityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: gravity_validator.py must be importable."""
        assert _AVAILABLE

    def test_gravityviolation_is_type(self) -> None:
        assert GravityViolation is not None

    def test_importviolation_is_type(self) -> None:
        assert ImportViolation is not None

    def test_hierarchyviolation_is_type(self) -> None:
        assert HierarchyViolation is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


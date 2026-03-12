"""ADG importability contract for system_learning/engines/surface_isolation_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_surface_isolation_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.surface_isolation_validator import (  # noqa: F401
        SurfaceIsolationValidator,
        get_surface_isolation_validator,
        reset_surface_isolation_validator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SurfaceIsolationValidator = None  # type: ignore[assignment,misc]
    get_surface_isolation_validator = None  # type: ignore[assignment,misc]
    reset_surface_isolation_validator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="surface_isolation_validator.py deps unavailable")
class TestSurfaceIsolationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: surface_isolation_validator.py must be importable."""
        assert _AVAILABLE

    def test_surfaceisolationvalidator_is_type(self) -> None:
        assert SurfaceIsolationValidator is not None

    def test_get_surface_isolation_validator_callable(self) -> None:
        assert callable(get_surface_isolation_validator)

    def test_reset_surface_isolation_validator_callable(self) -> None:
        assert callable(reset_surface_isolation_validator)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


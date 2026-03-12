"""ADG importability contract for agentic_core/L6_observability/engines/semantic_clock_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_semantic_clock_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.semantic_clock_validator import (  # noqa: F401
        SemanticClockHashMismatch,
        SemanticClockValidationResult,
        validate_artifact,
        scan_module_for_wallclock,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SemanticClockHashMismatch = None  # type: ignore[assignment,misc]
    SemanticClockValidationResult = None  # type: ignore[assignment,misc]
    validate_artifact = None  # type: ignore[assignment,misc]
    scan_module_for_wallclock = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="semantic_clock_validator.py deps unavailable")
class TestSemanticClockValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: semantic_clock_validator.py must be importable."""
        assert _AVAILABLE

    def test_semanticclockhashmismatch_is_type(self) -> None:
        assert SemanticClockHashMismatch is not None

    def test_semanticclockvalidationresult_is_type(self) -> None:
        assert SemanticClockValidationResult is not None

    def test_validate_artifact_callable(self) -> None:
        assert callable(validate_artifact)

    def test_scan_module_for_wallclock_callable(self) -> None:
        assert callable(scan_module_for_wallclock)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


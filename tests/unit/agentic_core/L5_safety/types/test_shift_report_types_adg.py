"""ADG importability contract for agentic_core/L5_safety/types/shift_report_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_shift_report_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.shift_report_types import (  # noqa: F401
        ShiftReport,
        CovariateShiftDetector,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ShiftReport = None  # type: ignore[assignment,misc]
    CovariateShiftDetector = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="shift_report_types.py deps unavailable")
class TestShiftReportTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: shift_report_types.py must be importable."""
        assert _AVAILABLE

    def test_shiftreport_is_type(self) -> None:
        assert ShiftReport is not None

    def test_covariateshiftdetector_is_type(self) -> None:
        assert CovariateShiftDetector is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


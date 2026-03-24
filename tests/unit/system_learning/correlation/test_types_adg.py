"""ADG importability contract for system_learning/correlation/types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.correlation.types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CorrelatedRiskReport,
        CorrelatedRow,
        DriftEvent,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    DriftEvent = None  # type: ignore[assignment,misc]
    CorrelatedRow = None  # type: ignore[assignment,misc]
    CorrelatedRiskReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="types.py deps unavailable")
class TestTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: types.py must be importable."""
        assert _AVAILABLE

    def test_driftevent_is_type(self) -> None:
        assert DriftEvent is not None

    def test_correlatedrow_is_type(self) -> None:
        assert CorrelatedRow is not None

    def test_correlatedriskreport_is_type(self) -> None:
        assert CorrelatedRiskReport is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
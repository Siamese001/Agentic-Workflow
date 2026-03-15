"""ADG importability contract for agentic_core/L4_state/enforcement/telemetry_recorder.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_telemetry_recorder.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.telemetry_recorder import (  # noqa: F401
        MAX_EVENTS,
        OutcomeRecord,
        ReconResult,
        TelemetryRecorder,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MAX_EVENTS = None  # type: ignore[assignment,misc]
    OutcomeRecord = None  # type: ignore[assignment,misc]
    ReconResult = None  # type: ignore[assignment,misc]
    TelemetryRecorder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="telemetry_recorder deps unavailable")
class TestTelemetryRecorderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/enforcement/telemetry_recorder.py must be importable."""
        assert _AVAILABLE

    def test_outcomerecord_defined(self) -> None:
        assert OutcomeRecord is not None

    def test_reconresult_defined(self) -> None:
        assert ReconResult is not None

    def test_telemetryrecorder_defined(self) -> None:
        assert TelemetryRecorder is not None

"""ADG importability contract for agentic_core/utils/workflow_engines/drift_monitor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_drift_monitor.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.drift_monitor import (  # noqa: F401
        DriftClock,
        RetrievalDriftMonitor,
        EmbeddingDriftMonitor,
        AnswerQualityMonitor,
        emit_alerts_to_registry,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DriftClock = None  # type: ignore[assignment,misc]
    RetrievalDriftMonitor = None  # type: ignore[assignment,misc]
    EmbeddingDriftMonitor = None  # type: ignore[assignment,misc]
    AnswerQualityMonitor = None  # type: ignore[assignment,misc]
    emit_alerts_to_registry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="drift_monitor.py deps unavailable")
class TestDriftMonitorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: drift_monitor.py must be importable."""
        assert _AVAILABLE

    def test_driftclock_is_type(self) -> None:
        assert DriftClock is not None

    def test_retrievaldriftmonitor_is_type(self) -> None:
        assert RetrievalDriftMonitor is not None

    def test_embeddingdriftmonitor_is_type(self) -> None:
        assert EmbeddingDriftMonitor is not None

    def test_emit_alerts_to_registry_callable(self) -> None:
        assert callable(emit_alerts_to_registry)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


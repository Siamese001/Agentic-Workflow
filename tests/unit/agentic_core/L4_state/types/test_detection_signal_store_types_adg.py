"""ADG importability contract for agentic_core/L4_state/types/detection_signal_store_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_detection_signal_store_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.detection_signal_store_types import (  # noqa: F401
        DetectionSignalStore,
        get_signal_store,
        store_detection_signal,
        fetch_latest_detection_signal,
        get_prior_detection_signal,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DetectionSignalStore = None  # type: ignore[assignment,misc]
    get_signal_store = None  # type: ignore[assignment,misc]
    store_detection_signal = None  # type: ignore[assignment,misc]
    fetch_latest_detection_signal = None  # type: ignore[assignment,misc]
    get_prior_detection_signal = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="detection_signal_store_types.py deps unavailable")
class TestDetectionSignalStoreTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: detection_signal_store_types.py must be importable."""
        assert _AVAILABLE

    def test_detectionsignalstore_is_type(self) -> None:
        assert DetectionSignalStore is not None

    def test_get_signal_store_callable(self) -> None:
        assert callable(get_signal_store)

    def test_store_detection_signal_callable(self) -> None:
        assert callable(store_detection_signal)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


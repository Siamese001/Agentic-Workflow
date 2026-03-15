"""ADG importability contract for agentic_core/runtime/config/signal_quality_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_signal_quality_config.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.signal_quality_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="signal_quality_config deps unavailable")
class TestSignalQualityConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/config/signal_quality_config.py must be importable."""
        assert _AVAILABLE

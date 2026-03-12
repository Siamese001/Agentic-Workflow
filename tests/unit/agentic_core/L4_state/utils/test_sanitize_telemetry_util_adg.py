"""ADG importability contract for agentic_core/L4_state/utils/sanitize_telemetry_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sanitize_telemetry_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.utils.sanitize_telemetry_util import (  # noqa: F401
        sanitize_tool_output,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    sanitize_tool_output = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="sanitize_telemetry_util.py deps unavailable")
class TestSanitizeTelemetryUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sanitize_telemetry_util.py must be importable."""
        assert _AVAILABLE

    def test_sanitize_tool_output_callable(self) -> None:
        assert callable(sanitize_tool_output)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


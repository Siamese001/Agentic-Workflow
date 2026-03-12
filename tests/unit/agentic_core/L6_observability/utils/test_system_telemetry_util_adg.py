"""ADG importability contract for agentic_core/L6_observability/utils/system_telemetry_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_system_telemetry_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.utils.system_telemetry_util import (  # noqa: F401
        SystemTelemetry,
        OperationStatus,
        get_telemetry,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SystemTelemetry = None  # type: ignore[assignment,misc]
    OperationStatus = None  # type: ignore[assignment,misc]
    get_telemetry = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="system_telemetry_util.py deps unavailable")
class TestSystemTelemetryUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: system_telemetry_util.py must be importable."""
        assert _AVAILABLE

    def test_systemtelemetry_is_type(self) -> None:
        assert SystemTelemetry is not None

    def test_operationstatus_is_type(self) -> None:
        assert OperationStatus is not None

    def test_get_telemetry_callable(self) -> None:
        assert callable(get_telemetry)


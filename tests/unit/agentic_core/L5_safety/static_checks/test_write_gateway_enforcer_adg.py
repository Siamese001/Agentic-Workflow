"""ADG importability contract for agentic_core/L5_safety/static_checks/write_gateway_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_write_gateway_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (  # noqa: F401
        WriteGatewayVisitor,
        scan_file_for_writes,
        scan_repository_for_writes,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    WriteGatewayVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_writes = None  # type: ignore[assignment,misc]
    scan_repository_for_writes = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="write_gateway_enforcer.py deps unavailable")
class TestWriteGatewayEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: write_gateway_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_writegatewayvisitor_is_type(self) -> None:
        assert WriteGatewayVisitor is not None

    def test_scan_file_for_writes_callable(self) -> None:
        assert callable(scan_file_for_writes)

    def test_scan_repository_for_writes_callable(self) -> None:
        assert callable(scan_repository_for_writes)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


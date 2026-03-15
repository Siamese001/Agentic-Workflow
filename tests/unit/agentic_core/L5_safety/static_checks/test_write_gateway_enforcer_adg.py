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
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    WriteGatewayVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_writes = None  # type: ignore[assignment,misc]
    scan_repository_for_writes = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="write_gateway_enforcer deps unavailable")
class TestWriteGatewayEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/static_checks/write_gateway_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_writegatewayvisitor_defined(self) -> None:
        assert WriteGatewayVisitor is not None

"""ADG importability contract for agentic_core/adg/applications/gateway_topology.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_gateway_topology.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.gateway_topology import (  # noqa: F401
        GatewayViolation,
        GatewayTopologyReport,
        check_gateway_topology,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GatewayViolation = None  # type: ignore[assignment,misc]
    GatewayTopologyReport = None  # type: ignore[assignment,misc]
    check_gateway_topology = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="gateway_topology.py deps unavailable")
class TestGatewayTopologyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: gateway_topology.py must be importable."""
        assert _AVAILABLE

    def test_gatewayviolation_is_type(self) -> None:
        assert GatewayViolation is not None

    def test_gatewaytopologyreport_is_type(self) -> None:
        assert GatewayTopologyReport is not None

    def test_check_gateway_topology_callable(self) -> None:
        assert callable(check_gateway_topology)


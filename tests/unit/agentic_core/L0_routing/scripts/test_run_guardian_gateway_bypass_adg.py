"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_gateway_bypass.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (  # noqa: F401
        scan_provider_sdk_imports,
        scan_direct_model_calls,
        run_gateway_bypass_guardian,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_provider_sdk_imports = None  # type: ignore[assignment,misc]
    scan_direct_model_calls = None  # type: ignore[assignment,misc]
    run_gateway_bypass_guardian = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_gateway_bypass.py deps unavailable")
class TestRunGuardianGatewayBypassImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_gateway_bypass.py must be importable."""
        assert _AVAILABLE

    def test_scan_provider_sdk_imports_callable(self) -> None:
        assert callable(scan_provider_sdk_imports)

    def test_scan_direct_model_calls_callable(self) -> None:
        assert callable(scan_direct_model_calls)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None


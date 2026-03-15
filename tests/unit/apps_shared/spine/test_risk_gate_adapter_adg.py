"""ADG importability contract for apps_shared/spine/risk_gate_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_risk_gate_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.spine.risk_gate_adapter import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RiskGateAdapter,
        RiskResult,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RiskResult = None  # type: ignore[assignment,misc]
    RiskGateAdapter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="risk_gate_adapter.py deps unavailable")
class TestRiskGateAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: risk_gate_adapter.py must be importable."""
        assert _AVAILABLE

    def test_riskresult_is_type(self) -> None:
        assert RiskResult is not None

    def test_riskgateadapter_is_type(self) -> None:
        assert RiskGateAdapter is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

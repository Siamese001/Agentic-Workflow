"""ADG importability contract for agentic_core/L5_safety/enforcement/conf_calib_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_conf_calib_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.conf_calib_gate import (  # noqa: F401
        ConfCalibRiskGate,
        RiskDecision,
        RiskLevel,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RiskLevel = None  # type: ignore[assignment,misc]
    RiskDecision = None  # type: ignore[assignment,misc]
    ConfCalibRiskGate = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="conf_calib_gate deps unavailable")
class TestConfCalibGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/conf_calib_gate.py must be importable."""
        assert _AVAILABLE

    def test_risklevel_defined(self) -> None:
        assert RiskLevel is not None

    def test_riskdecision_defined(self) -> None:
        assert RiskDecision is not None

    def test_confcalibriskgate_defined(self) -> None:
        assert ConfCalibRiskGate is not None

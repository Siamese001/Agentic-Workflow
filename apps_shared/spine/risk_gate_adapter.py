"""
Risk Gate Adapter — bridges ConfCalibRiskGate to the spine's _RiskResult interface.

ConfCalibRiskGate.evaluate() returns RiskDecision(allow, level, reasons).
The spine adapters expect an object with a single bool attribute: allow.

This adapter wraps ConfCalibRiskGate and returns a RiskResult compatible
with the spine's existing _RiskResult contract.
Falls back to allow=True null behavior if ConfCalibRiskGate cannot be imported.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RiskResult:
    """
    Minimal risk result compatible with spine adapter _RiskResult contract.

    Extends the null stub type so existing spine code works unchanged.
    Carries the full decision context for observability.
    """
    allow: bool
    level: str = 'LOW'
    reasons: tuple[str, ...] = ()

def _build_real_gate():
    from agentic_core.L5_safety.enforcement.conf_calib_gate import ConfCalibRiskGate
    return ConfCalibRiskGate

class RiskGateAdapter:
    """
    Adapter wrapping ConfCalibRiskGate for use in spine adapters.

    Converts RiskDecision → RiskResult so existing spine wiring requires
    no changes to its evaluate() call site.
    Falls back to allow=True when the real gate is unavailable.
    """

    def __init__(self) -> None:
        try:
            ConfCalibRiskGate = _build_real_gate()
            self._gate = ConfCalibRiskGate()
            self._real = True
        except ImportError:
            logger.warning('ConfCalibRiskGate unavailable; using null fallback (allow=True)')
            self._gate = None
            self._real = False

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> RiskResult:
        """
        Evaluate risk for payload and D0 injections.

        Args:
            payload_like: Object with optional .sanitized and .check_ids attributes
            d0_injections: D0 injection string (checked for "DENY_EXECUTION")

        Returns:
            RiskResult with allow, level, and reasons from the real gate,
            or RiskResult(allow=True) when gate unavailable.
        """
        if not self._real:
            return RiskResult(allow=True)
        d0_str = d0_injections if isinstance(d0_injections, str) else str(d0_injections)
        decision = self._gate.evaluate(payload_like=payload_like, d0_injections=d0_str)
        return RiskResult(allow=decision.allow, level=decision.level.value, reasons=decision.reasons)

    @property
    def is_real(self) -> bool:
        """True if backed by the real ConfCalibRiskGate, False for null fallback."""
        return self._real

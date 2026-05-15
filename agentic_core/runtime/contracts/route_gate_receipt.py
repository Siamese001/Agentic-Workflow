"""Typed route-gate receipts for L0 routing output.

TEMPORARY_THIN_ADAPTER — per plan p3.2_apps-rg-l0-critical-gaps-remediation-a3f8e1
until canonical 00C GateVerdict wiring lands on this path.

These receipts are intentionally generic (no resume-specific enums).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GateVerdictLiteral = Literal["PASS", "UNKNOWN", "FAIL", "WARN", "NOT_APPLICABLE"]


@dataclass(frozen=True, slots=True)
class RouteGateReceipt:
    """Single gate evaluation surface for RouteContract.route_gate_receipts."""

    gate_id: str
    verdict: GateVerdictLiteral
    score: float
    facts_present: bool
    adapter_kind: str = "TEMPORARY_THIN_ADAPTER"
    reason: str = ""

    def to_runtime_gate_ref(self) -> str:
        """Stable string for ManagedWorkflowRunner.runtime_gate_refs merge."""
        return f"{self.gate_id}:{self.verdict}:{self.score:.3f}"

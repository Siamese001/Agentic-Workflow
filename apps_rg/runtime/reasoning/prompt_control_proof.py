"""Deterministic interpretation of ReasoningExecutionReceipt for apps_rg lane proof eligibility."""

from __future__ import annotations

from typing import Any


def reasoning_receipt_denies_quality_certification(receipt: Any) -> tuple[bool, list[str]]:
    """Return (denied, reasons) when gateway receipt proves certification was denied or aggregate-blocked."""
    if receipt is None:
        return False, []
    if not isinstance(receipt, dict):
        return False, []
    reasons: list[str] = []
    if receipt.get("aggregate_blocked") is True:
        reasons.append("aggregate_blocked")
    if receipt.get("quality_certification_denied") is True:
        reasons.append("quality_certification_denied")
    return bool(reasons), reasons


def summarize_reasoning_receipt_for_bundle(receipt: Any) -> dict[str, Any]:
    """Compact snapshot for L2 / evidence (no secrets)."""
    denied, reasons = reasoning_receipt_denies_quality_certification(receipt)
    return {
        "present": isinstance(receipt, dict),
        "quality_certification_denied": bool(isinstance(receipt, dict) and receipt.get("quality_certification_denied")),
        "aggregate_blocked": bool(isinstance(receipt, dict) and receipt.get("aggregate_blocked")),
        "proof_blocking_reasons": reasons,
        "blocks_proof_eligible_lane": denied,
    }


__all__ = [
    "reasoning_receipt_denies_quality_certification",
    "summarize_reasoning_receipt_for_bundle",
]

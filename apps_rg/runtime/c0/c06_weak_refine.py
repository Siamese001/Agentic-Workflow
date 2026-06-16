"""C0.6 — retired weak-support refinement shim.

The live evidence room no longer performs receipt-only refinement. Until a real
bounded C0.2 retry is implemented, this module is compatibility-only and must
not claim that a retry happened.
"""

from __future__ import annotations

from typing import Any

def maybe_c06_weak_refine(
    *,
    support_status: str,
    atoms: list[dict[str, Any]],
    retrieval_plan: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return atoms unchanged with an explicit retired/disabled receipt."""
    del support_status, retrieval_plan
    receipt = {
        "schema_version": "c06_weak_refine_v1",
        "attempted": False,
        "disabled": True,
        "reason": "retired_receipt_only_refine_use_bounded_c02_retry_when_implemented",
    }
    return atoms, receipt


__all__ = ["maybe_c06_weak_refine"]

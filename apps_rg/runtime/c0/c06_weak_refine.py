"""C0.6 — one bounded weak-support refinement retry."""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import SUPPORT_STATUS_WEAK


def maybe_c06_weak_refine(
    *,
    support_status: str,
    atoms: list[dict[str, Any]],
    retrieval_plan: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Single retry: broaden supporting targets only — no policy/auth changes."""
    receipt = {
        "schema_version": "c06_weak_refine_v1",
        "attempted": False,
        "reason": "",
    }
    if support_status != SUPPORT_STATUS_WEAK or len(atoms) >= 3:
        return atoms, receipt
    receipt["attempted"] = True
    receipt["reason"] = "weak_support_broadened_retrieval_targets_once"
    plan = dict(retrieval_plan.get("retrieval_targets") or {})
    secondary = list(plan.get("secondary_targets") or [])
    secondary.append("background_support_atoms")
    plan["secondary_targets"] = secondary
    retrieval_plan = {**retrieval_plan, "retrieval_targets": plan}
    return atoms, receipt


__all__ = ["maybe_c06_weak_refine"]

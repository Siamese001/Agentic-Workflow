"""Repair authority helpers for W1.1 singleness tests."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.section_repair_ledger import (
    KIND_DETERMINISTIC_REWRITE,
    KIND_MECHANICAL,
    KIND_REGEN_LLM,
    ledger_blocks_product_pass,
)

_GRAPH_ONLY_QUALITY_OP = "graph_only_generation_quality_repair"


def count_regen_llm_replaced(repairs: list[dict[str, Any]]) -> int:
    return sum(
        1
        for r in repairs
        if r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
    )


def assert_single_repair_authority_path(ledger: dict[str, Any] | None) -> tuple[bool, str]:
    """Return (ok, reason). Enforces max one LLM regen that replaces L2 before X2."""
    if ledger is None:
        return True, ""
    repairs = list(ledger.get("repairs") or [])
    regen_count = count_regen_llm_replaced(repairs)
    if regen_count > 1:
        return False, f"multiple_regen_llm_replaced_l2:{regen_count}"
    # Multiple active authority paths without ordered ledger
    regen_ops = [r.get("operation") for r in repairs if r.get("kind") == KIND_REGEN_LLM]
    if len(regen_ops) > 1 and regen_count >= 1:
        return False, f"multiple_regen_operations:{regen_ops}"
    if not ledger.get("product_fail_closed"):
        return True, ""
    blocked, block_reason = ledger_blocks_product_pass(ledger)
    if blocked:
        return False, block_reason
    return True, ""


def mechanical_repairs_same_authority(repairs: list[dict[str, Any]]) -> bool:
    """Non-LLM repairs must be mechanical or authorized deterministic rewrite only."""
    for r in repairs:
        kind = r.get("kind")
        if kind == KIND_REGEN_LLM:
            continue
        if kind == KIND_MECHANICAL:
            continue
        if kind == KIND_DETERMINISTIC_REWRITE:
            op = str(r.get("operation") or "")
            if op == _GRAPH_ONLY_QUALITY_OP:
                continue
            return False
    return True


__all__ = [
    "assert_single_repair_authority_path",
    "count_regen_llm_replaced",
    "mechanical_repairs_same_authority",
]

"""Apps-owned judge-directed regen loop orchestration (ADR-086, plan d8f3a1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.L2_execution.regen.judge_directed_regen import (
    DEFAULT_STEP_ORDER,
    JudgeDirectedRegenPlan,
    JudgeDirectedRegenStep,
)

POST_REGEN_X2_REPAIR_ELIGIBLE_GATES = frozenset(
    {
        "x2_exec_summary_meta_filler_zero",
        "x2_source_sensitive_phrases_supported",
        "x2_exec_summary_mechanical_opener_stack_zero",
        "x2_exec_summary_no_mechanism_inventory",
    },
)


def default_regen_loop_plan() -> JudgeDirectedRegenPlan:
    return JudgeDirectedRegenPlan(steps=DEFAULT_STEP_ORDER)


def prepare_parsed_after_judge_regen(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    plan_facts: list[dict[str, Any]],
    artifact_dir: Path | None = None,
    target_company: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Deterministic post-LLM prepare before X2 (voice, ledger, authority)."""
    from apps_rg.runtime.sections.section_authority_repairs import (
        apply_exec_summary_display_authority_repairs,
    )
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        finalize_executive_summary_coherence,
        strip_unsupported_source_sensitive_prose,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_regen_prepare_v1",
    }
    out = dict(parsed)
    out, ss_receipt = strip_unsupported_source_sensitive_prose(
        out,
        selected_facts=plan_facts,
    )
    receipt["source_sensitive_strip"] = ss_receipt
    out = apply_exec_summary_display_authority_repairs(
        out,
        allowed_fact_ids=allowed_fact_ids,
        plan_facts=plan_facts,
        artifact_dir=artifact_dir,
        target_company=target_company,
    )
    out, fin_receipt = finalize_executive_summary_coherence(
        out,
        selected_facts=plan_facts,
    )
    receipt["finalize_coherence"] = fin_receipt
    return out, receipt


def _unique_source_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if s:
                ids.add(s)
    return ids


def preserve_judge_regen_claim_ledger_from_baseline(
    regen_parsed: dict[str, Any],
    *,
    baseline_parsed: dict[str, Any],
    allowed_fact_ids: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Restore baseline ledger rows when regen drops allowed source_fact_ids (coverage monotonicity)."""
    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_regen_preserve_ledger_v1",
        "restored_fact_ids": [],
        "restored_row_count": 0,
    }
    out = dict(regen_parsed)
    baseline_ledger = [
        dict(r) for r in (baseline_parsed.get("claim_ledger") or []) if isinstance(r, dict)
    ]
    regen_ledger = [dict(r) for r in (out.get("claim_ledger") or []) if isinstance(r, dict)]
    if not baseline_ledger:
        return out, receipt

    baseline_facts = _unique_source_fact_ids(baseline_ledger)
    regen_facts = _unique_source_fact_ids(regen_ledger)
    allowed = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
    missing_set = {
        fid
        for fid in (baseline_facts - regen_facts)
        if not allowed or fid in allowed
    }
    if not missing_set:
        return out, receipt

    regen_fact_sets = [_unique_source_fact_ids([row]) for row in regen_ledger]
    restored = 0
    restored_fact_ids: set[str] = set()
    for row in baseline_ledger:
        row_facts = _unique_source_fact_ids([row])
        if not row_facts or not row_facts <= missing_set:
            continue
        if any(row_facts <= existing for existing in regen_fact_sets if existing):
            continue
        regen_ledger.append(dict(row))
        regen_fact_sets.append(row_facts)
        restored += 1
        restored_fact_ids |= row_facts

    if restored:
        out["claim_ledger"] = regen_ledger
        receipt["restored_fact_ids"] = sorted(restored_fact_ids)
        receipt["restored_row_count"] = restored
        receipt["repaired"] = True
    return out, receipt


def write_judge_regen_x2_snapshot(
    artifact_dir: Path,
    filename: str,
    x2_gates: list[dict[str, Any]],
    *,
    label: str = "",
) -> Path:
    """Persist labeled X2 gate snapshot for hostile verifier ordering proof."""
    from apps_rg.runtime.sections.section_x2_gate_outputs import write_x2_gate_outputs

    path = artifact_dir / filename
    write_x2_gate_outputs(path, x2_gates, snapshot_label=label)
    return path


def failed_gate_ids(x2_gates: list[dict[str, Any]]) -> list[str]:
    return [
        str(g.get("gate_id") or "")
        for g in x2_gates
        if isinstance(g, dict) and not g.get("pass")
    ]


def post_regen_x2_repair_eligible(failed_gates: list[dict[str, Any]]) -> bool:
    """True when failed gates are shape/voice-only (one bounded repair allowed)."""
    ids = {g for g in failed_gate_ids(failed_gates) if g}
    if not ids:
        return False
    return ids.issubset(POST_REGEN_X2_REPAIR_ELIGIBLE_GATES)


def extend_regen_thread_after_success(
    regen_messages: list[dict[str, str]],
    raw_output: str,
) -> list[dict[str, str]]:
    """Append assistant turn only — next cycle uses core prescriptive delta, not legacy user block."""
    out = list(regen_messages)
    if raw_output:
        out.append({"role": "assistant", "content": raw_output})
    return out


__all__ = [
    "DEFAULT_STEP_ORDER",
    "JudgeDirectedRegenPlan",
    "JudgeDirectedRegenStep",
    "POST_REGEN_X2_REPAIR_ELIGIBLE_GATES",
    "default_regen_loop_plan",
    "extend_regen_thread_after_success",
    "failed_gate_ids",
    "post_regen_x2_repair_eligible",
    "preserve_judge_regen_claim_ledger_from_baseline",
    "prepare_parsed_after_judge_regen",
    "write_judge_regen_x2_snapshot",
]

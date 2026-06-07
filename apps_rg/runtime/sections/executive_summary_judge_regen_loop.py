"""Apps-owned judge-directed regen loop orchestration (ADR-086, plan d8f3a1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_METRIC_PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%", re.IGNORECASE)

from apps_rg.runtime.sections.executive_summary_regen_support import (
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

    from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
        _sanitize_deprecated_commercialization_thread,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_regen_prepare_v1",
    }
    out = dict(parsed)
    _resume = str(out.get("resume_display_text") or "")
    if re.search(r"\bcommercialization\b", _resume, re.IGNORECASE):
        out["resume_display_text"] = _sanitize_deprecated_commercialization_thread(_resume)
        receipt["commercialization_thread_sanitize"] = True
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


def resume_display_text_from_regen_messages(
    messages: list[dict[str, str]],
) -> str:
    """Parse resume_display_text from the latest assistant JSON turn in the regen thread."""
    import json

    for msg in reversed(messages):
        if str(msg.get("role") or "").lower() != "assistant":
            continue
        raw = str(msg.get("content") or "").strip()
        if not raw.startswith("{"):
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            text = str(parsed.get("resume_display_text") or "").strip()
            if text:
                return text
    return ""


def advance_regen_thread_for_next_cycle(
    regen_messages: list[dict[str, str]],
    *,
    raw_output: str,
    x1d_judges: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """After rescore (even when G3 rejects publish): anchor next cycle on latest regen + judges."""
    out_messages = extend_regen_thread_after_success(regen_messages, raw_output)
    return out_messages, list(x1d_judges)


def _normalize_pct_token(raw: str) -> str:
    return re.sub(r"\s+", "", str(raw or "").lower())


def _percent_tokens_in_text(text: str) -> list[str]:
    return [_normalize_pct_token(m) for m in _METRIC_PCT_RE.findall(str(text or ""))]


def _fact_support_blob(fact: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("claim_text", "achievement_summary", "metric_raw", "text"):
        val = fact.get(key)
        if val:
            parts.append(str(val))
    for val in fact.get("metric_values") or []:
        if val:
            parts.append(str(val))
    return " ".join(parts)


def _facts_index(plan_facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in plan_facts:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
        if fid:
            out[fid] = row
    return out


def _replace_percent_token(text: str, before_pct: str, after_pct: str) -> tuple[str, int]:
    before_num = before_pct.rstrip("%").strip()
    after_num = after_pct.rstrip("%").strip()
    if not before_num or not after_num or before_num == after_num:
        return text, 0
    pattern = re.compile(rf"\b{re.escape(before_num)}\s*%", re.IGNORECASE)
    return pattern.subn(f"{after_num}%", text)


def _authoritative_percent_for_sources(
    source_fact_ids: list[str],
    facts_by_id: dict[str, dict[str, Any]],
) -> tuple[str | None, str | None, str]:
    """Return (canonical_pct, source_fact_id, status)."""
    per_fact: dict[str, set[str]] = {}
    for fid in source_fact_ids:
        fact = facts_by_id.get(fid)
        if not fact:
            continue
        tokens = set(_percent_tokens_in_text(_fact_support_blob(fact)))
        if tokens:
            per_fact[fid] = tokens

    if not per_fact:
        return None, None, "no_metric_in_cited_facts"

    union: set[str] = set()
    for tokens in per_fact.values():
        union |= tokens
    if len(union) != 1:
        return None, None, "conflicting_metrics_across_cited_facts"

    canonical = next(iter(union))
    holders = [fid for fid, tokens in per_fact.items() if canonical in tokens]
    if len(holders) != 1:
        return None, None, "ambiguous_multiple_source_facts"
    return canonical, holders[0], "ok"


def sync_claim_ledger_metrics_from_facts(
    parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """G1 — deterministic ledger metric sync on the candidate being evaluated (fail-closed)."""
    receipt: dict[str, Any] = {
        "schema": "executive_summary_g1_ledger_metric_sync_v1",
        "passed": True,
        "reject_gate": None,
        "row_repairs": [],
        "repairs_applied": 0,
    }
    out = dict(parsed)
    ledger = [dict(r) for r in (out.get("claim_ledger") or []) if isinstance(r, dict)]
    if not ledger:
        return out, receipt

    allowed = {str(x).strip() for x in (allowed_fact_ids or set()) if str(x).strip()}
    facts_by_id = _facts_index(plan_facts)
    display = str(out.get("resume_display_text") or "")
    replacements: dict[str, str] = {}

    for idx, row in enumerate(ledger):
        row_id = str(row.get("claim_id") or row.get("row_id") or f"row_{idx + 1}")
        claim_text = str(row.get("claim_text") or "")
        claim_field = str(row.get("claim") or "")
        source_ids = [
            str(x).strip()
            for x in (row.get("source_fact_ids") or [])
            if str(x).strip() and (not allowed or str(x).strip() in allowed)
        ]
        if not source_ids:
            receipt["passed"] = False
            receipt["reject_gate"] = "ledger_metric_sync_ambiguous"
            receipt["failure_reason"] = f"{row_id}: no_allowed_source_fact_ids"
            return out, receipt

        canonical, source_fact_id, status = _authoritative_percent_for_sources(
            source_ids,
            facts_by_id,
        )
        if status != "ok" or not canonical or not source_fact_id:
            row_pcts = set(_percent_tokens_in_text(claim_text))
            claim_pcts = set(_percent_tokens_in_text(claim_field))
            if not row_pcts and not claim_pcts:
                continue
            receipt["passed"] = False
            receipt["reject_gate"] = "ledger_metric_sync_ambiguous"
            receipt["failure_reason"] = f"{row_id}: {status}"
            return out, receipt

        mismatches: list[tuple[str, str]] = []
        for token in set(_percent_tokens_in_text(claim_text)):
            if token != canonical:
                mismatches.append((token, canonical))
        for token in set(_percent_tokens_in_text(claim_field)):
            if token != canonical:
                pair = (token, canonical)
                if pair not in mismatches:
                    mismatches.append(pair)

        if not mismatches:
            continue

        for before_pct, after_pct in mismatches:
            if before_pct in replacements and replacements[before_pct] != after_pct:
                receipt["passed"] = False
                receipt["reject_gate"] = "ledger_metric_sync_ambiguous"
                receipt["failure_reason"] = (
                    f"{row_id}: conflicting display replacements for {before_pct}"
                )
                return out, receipt
            replacements[before_pct] = after_pct
            new_claim_text, n_ct = _replace_percent_token(claim_text, before_pct, after_pct)
            new_claim_field, n_cf = _replace_percent_token(claim_field, before_pct, after_pct)
            if n_ct or n_cf:
                claim_text = new_claim_text
                claim_field = new_claim_field
                row["claim_text"] = claim_text
                if claim_field:
                    row["claim"] = claim_field
                receipt["row_repairs"].append(
                    {
                        "row_id": row_id,
                        "before_metric": before_pct,
                        "after_metric": after_pct,
                        "source_fact_id": source_fact_id,
                        "repair_reason": "claim_text_metric_mismatch_single_source",
                    },
                )
                receipt["repairs_applied"] = int(receipt["repairs_applied"]) + 1

    display_repairs: list[dict[str, Any]] = []
    for before_pct, after_pct in replacements.items():
        display, n_disp = _replace_percent_token(display, before_pct, after_pct)
        if n_disp:
            display_repairs.append(
                {
                    "before_metric": before_pct,
                    "after_metric": after_pct,
                    "replacements_in_display": n_disp,
                },
            )
    if display_repairs:
        receipt["display_repairs"] = display_repairs

    out["claim_ledger"] = ledger
    if display != str(out.get("resume_display_text") or ""):
        out["resume_display_text"] = display
    return out, receipt


def snapshot_regen_candidate(
    *,
    raw_output: str,
    parsed: dict[str, Any],
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Working copy of the latest judge-regen draft (retained when post-regen X2 fails)."""
    out: dict[str, Any] = {
        "raw_output": raw_output,
        "parsed": dict(parsed),
        "resume_display_text": resume_display_text,
        "claim_ledger": [dict(r) for r in claim_ledger if isinstance(r, dict)],
    }
    if x2_gates is not None:
        out["x2_gates"] = [dict(g) for g in x2_gates if isinstance(g, dict)]
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
    "snapshot_regen_candidate",
    "sync_claim_ledger_metrics_from_facts",
    "write_judge_regen_x2_snapshot",
]

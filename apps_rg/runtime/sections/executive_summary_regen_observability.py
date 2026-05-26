"""W4.2 — judge regen cycles observability (feedback pack, transport, cycle field semantics)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    _flatten_delta_sections,
    _is_droppable_guard_delta_line,
    _soft_failed_model_judges,
    _verbatim_soft_failed_judge_feedback_lines,
)


def pack_judge_feedback_with_stats(
    sections: dict[str, list[str]],
) -> tuple[list[str], dict[str, Any]]:
    """Pack all delta lines (full judge feedback; no token truncation)."""
    raw_feedback = [str(ln) for ln in (sections.get("judge_feedback") or []) if str(ln).strip()]
    packed = _flatten_delta_sections(sections)
    included_feedback = [ln for ln in packed if ln in raw_feedback]
    stats = {
        "judge_feedback_lines_total": len(raw_feedback),
        "judge_feedback_lines_included": len(included_feedback),
        "judge_feedback_lines_dropped": 0,
        "dropped_reason": None,
    }
    return packed, stats


def audit_judge_feedback_pack(
    x1d_judges: list[Any],
) -> dict[str, Any]:
    """Feedback pack stats for a regen cycle (pre-dispatch)."""
    soft = _soft_failed_model_judges(x1d_judges)
    sections = {
        "judge_feedback": _verbatim_soft_failed_judge_feedback_lines(soft),
        "dimension": [],
        "floors": [],
        "guards": [],
    }
    _packed, stats = pack_judge_feedback_with_stats(sections)
    stats["droppable_guard_lines_skipped_in_count"] = sum(
        1 for ln in _packed if _is_droppable_guard_delta_line(ln)
    )
    return stats


def transport_stats_for_cycle(artifact_dir: Path | str | None, cycle_index: int) -> dict[str, int]:
    """Count Qwen transport rows for judge_regen at ``cycle_index`` (0-based, matches ledger)."""
    if artifact_dir is None:
        return {"transport_attempts_per_cycle": 0, "semantic_rewrite_attempts": 0}
    from apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch import regen_budget_ledger

    ledger = regen_budget_ledger(artifact_dir)
    rows = [
        c
        for c in ledger.calls
        if isinstance(c, dict)
        and str(c.get("phase") or "") == "judge_regen"
        and int(c.get("cycle_index") or -1) == int(cycle_index)
    ]
    transport_attempts = sum(max(1, int(r.get("attempt_index") or 0) + 1) for r in rows) if rows else 0
    semantic = sum(1 for r in rows if r.get("transport_dispatched"))
    return {
        "transport_attempts_per_cycle": transport_attempts,
        "semantic_rewrite_attempts": semantic,
    }


def normalize_cycle_record_observability(cycle_record: dict[str, Any]) -> dict[str, Any]:
    """Apply W4.2 field semantics: ``draft_parse_ok`` vs post-gate ``accepted``."""
    out = dict(cycle_record)
    if "draft_parse_ok" not in out and "accepted" in out and not out.get("publish_eligible"):
        out["draft_parse_ok"] = bool(out.get("accepted"))
    if out.get("publish_eligible") and out.get("g3_passed") is not False:
        if "draft_parse_ok" not in out:
            out["draft_parse_ok"] = True
        out["accepted"] = True
    else:
        out["accepted"] = bool(out.get("draft_parse_ok")) and bool(out.get("publish_eligible"))
    return out


def finalize_judge_regen_cycles_receipt(
    receipt: dict[str, Any],
    *,
    artifact_dir: Path | str | None = None,
    scratch_candidate_digest: str = "",
    published_candidate_digest: str = "",
) -> dict[str, Any]:
    """Enrich cycles receipt with W4.2 observability rollup fields."""
    out = dict(receipt)
    cycles = [normalize_cycle_record_observability(c) for c in (out.get("cycles") or []) if isinstance(c, dict)]
    out["cycles"] = cycles
    out["judge_regen_cycles"] = list(cycles)
    baseline = str(scratch_candidate_digest or "").strip()
    if not baseline and cycles:
        first = cycles[0]
        baseline = str(first.get("candidate_digest") or first.get("publishable_baseline_hash") or "")
    if baseline:
        out["publishable_baseline_hash"] = hashlib.sha256(baseline.encode()).hexdigest()[:16]
    else:
        out["publishable_baseline_hash"] = ""
    published = str(published_candidate_digest or out.get("published_candidate_digest") or "").strip()
    if published:
        out["published_candidate_digest"] = published
    last_regen = next((c for c in reversed(cycles) if c.get("candidate_digest")), None)
    if last_regen:
        out["rewrite_from"] = str(last_regen.get("candidate_digest") or "")
    else:
        out["rewrite_from"] = baseline or "scratch"
    out["use_rejected_as_negative_example"] = bool(
        out.get("regen_outcome") == "no_acceptable_candidate"
        and any(c.get("draft_parse_ok") for c in cycles)
    )
    if artifact_dir is not None:
        transport_total = 0
        semantic_total = 0
        for row in cycles:
            cyc = int(row.get("cycle") or 0)
            if cyc < 1:
                continue
            stats = transport_stats_for_cycle(artifact_dir, cyc - 1)
            row["transport_attempts_per_cycle"] = stats["transport_attempts_per_cycle"]
            row["semantic_rewrite_attempts"] = stats["semantic_rewrite_attempts"]
            transport_total += stats["transport_attempts_per_cycle"]
            semantic_total += stats["semantic_rewrite_attempts"]
        out["transport_attempts_total"] = transport_total
        out["semantic_rewrite_attempts_total"] = semantic_total
    return out


__all__ = [
    "audit_judge_feedback_pack",
    "finalize_judge_regen_cycles_receipt",
    "normalize_cycle_record_observability",
    "pack_judge_feedback_with_stats",
    "transport_stats_for_cycle",
]

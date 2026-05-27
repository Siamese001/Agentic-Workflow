"""W4.2 / W5 — judge regen cycles observability, per-cycle artifacts, convergence guard."""

from __future__ import annotations

import hashlib
import json
import re
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
    *,
    max_lines: int | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Pack delta lines; truncate judge_feedback tail when over core line budget."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        judge_regen_max_delta_lines,
        regen_artificial_caps_enabled,
    )

    if not regen_artificial_caps_enabled():
        line_cap = None
    else:
        line_cap = int(max_lines if max_lines is not None else judge_regen_max_delta_lines())
    raw_feedback = [str(ln) for ln in (sections.get("judge_feedback") or []) if str(ln).strip()]
    packed = _flatten_delta_sections(
        sections,
        max_lines=line_cap if line_cap is not None else None,
    )
    included_feedback = [ln for ln in packed if ln in raw_feedback]
    dropped = max(0, len(raw_feedback) - len(included_feedback))
    stats = {
        "judge_feedback_lines_total": len(raw_feedback),
        "judge_feedback_lines_included": len(included_feedback),
        "judge_feedback_lines_dropped": dropped,
        "dropped_reason": "delta_line_budget_tail_truncation" if dropped else None,
        "regen_caps_enabled": regen_artificial_caps_enabled(),
        "max_delta_lines": line_cap,
        "packed_delta_lines": len(packed),
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


REGEN_STOPPED_REASON_CONVERGED = "regen_converged"
REGEN_STOPPED_REASON_X2_STUCK = "x2_stuck_same_failure"
STUCK_LOOP_N_CYCLES = 2
X2_GATE_CLAIM_FIELD_MAPS = "x2_claim_field_maps_to_display_sentence"

_ROW_INDEX_RE = re.compile(r"row_(\d+)")


def x2_failed_row_indexes_from_gates(x2_gates: list[dict[str, Any]] | None) -> tuple[int, ...]:
    """Parse ``row_N`` tokens from the claim-field X2 gate failure text."""
    if not x2_gates:
        return ()
    indexes: list[int] = []
    for gate in x2_gates:
        if not isinstance(gate, dict) or gate.get("pass"):
            continue
        if str(gate.get("gate_id") or "") != X2_GATE_CLAIM_FIELD_MAPS:
            continue
        blob = " ".join(
            (
                str(gate.get("failure_reason") or ""),
                str(gate.get("observed_value") or ""),
            ),
        )
        for match in _ROW_INDEX_RE.finditer(blob):
            indexes.append(int(match.group(1)))
    return tuple(sorted(set(indexes)))


def regen_failure_signature_from_cycle_record(
    cycle_record: dict[str, Any],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Stable signature for stuck-loop detection: sorted gate ids + row indexes."""
    gate_ids = tuple(
        sorted(
            {
                str(gate_id)
                for gate_id in (cycle_record.get("post_regen_x2_failed_gate_ids") or [])
                if str(gate_id).strip()
            },
        ),
    )
    rows_raw = cycle_record.get("post_regen_x2_failed_row_indexes")
    if rows_raw is not None:
        row_indexes = tuple(sorted({int(idx) for idx in rows_raw}))
    else:
        row_indexes = ()
    return gate_ids, row_indexes


def regen_failure_signature(
    *,
    cycle_record: dict[str, Any] | None = None,
    x2_gates: list[dict[str, Any]] | None = None,
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Build failure signature from a cycle row and/or post-regen X2 gate list."""
    record = dict(cycle_record or {})
    if x2_gates is not None:
        record["post_regen_x2_failed_gate_ids"] = [
            str(g.get("gate_id") or "")
            for g in x2_gates
            if isinstance(g, dict) and not g.get("pass")
        ]
        row_indexes = x2_failed_row_indexes_from_gates(x2_gates)
        if row_indexes:
            record["post_regen_x2_failed_row_indexes"] = list(row_indexes)
    return regen_failure_signature_from_cycle_record(record)


def trailing_same_failure_signature_count(
    prior_cycles: list[dict[str, Any]],
    signature: tuple[tuple[str, ...], tuple[int, ...]],
) -> int:
    """Count trailing prior cycles whose failure signature equals ``signature``."""
    if not signature[0]:
        return 0
    count = 0
    for row in reversed(prior_cycles):
        if not isinstance(row, dict):
            break
        if regen_failure_signature_from_cycle_record(row) == signature:
            count += 1
        else:
            break
    return count


def detect_x2_stuck_same_failure(
    cycles_receipt: dict[str, Any],
    signature: tuple[tuple[str, ...], tuple[int, ...]],
    *,
    n_cycles: int = STUCK_LOOP_N_CYCLES,
) -> bool:
    """True when ``signature`` repeats for ``n_cycles`` consecutive cycles (incl. current)."""
    if not signature[0]:
        return False
    prior = [c for c in (cycles_receipt.get("cycles") or []) if isinstance(c, dict)]
    trailing = trailing_same_failure_signature_count(prior, signature)
    return (trailing + 1) >= int(n_cycles)


def build_regen_lane_stats(cycles_receipt: dict[str, Any]) -> dict[str, Any]:
    """Rollup for Notion review / lane receipts."""
    stopped = str(cycles_receipt.get("stopped_reason") or "").strip()
    stuck = stopped == REGEN_STOPPED_REASON_X2_STUCK
    last_sig: dict[str, Any] | None = None
    cycles = [c for c in (cycles_receipt.get("cycles") or []) if isinstance(c, dict)]
    if cycles:
        gate_ids, row_indexes = regen_failure_signature_from_cycle_record(cycles[-1])
        last_sig = {
            "failing_gate_ids": list(gate_ids),
            "row_indexes": list(row_indexes),
        }
    stuck_signature = cycles_receipt.get("stuck_signature")
    return {
        "stuck_loop_detected": stuck,
        "stopped_reason": stopped or None,
        "stuck_signature": stuck_signature if stuck else None,
        "last_failure_signature": last_sig,
    }


def regen_output_hash_from_receipt(judge_remediation_receipt: dict[str, Any]) -> str:
    return str(judge_remediation_receipt.get("regen_output_hash") or "").strip()


def persist_regen_cycle_artifacts(
    artifact_dir: Path | str,
    cycle_num: int,
    *,
    judge_remediation_receipt: dict[str, Any] | None = None,
    x2_gates: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Write per-cycle regen artifacts (W5.1) without replacing prior cycle files."""
    base = Path(artifact_dir)
    paths: dict[str, str] = {}
    if judge_remediation_receipt is not None:
        receipt_path = base / f"judge_remediation_receipt_cycle_{cycle_num}.json"
        receipt_path.write_text(
            json.dumps(judge_remediation_receipt, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        paths["judge_remediation_receipt_cycle"] = str(receipt_path)
    if x2_gates is not None:
        from apps_rg.runtime.sections.executive_summary_judge_regen_loop import (
            write_judge_regen_x2_snapshot,
        )

        x2_path = write_judge_regen_x2_snapshot(
            base,
            f"x2_gate_outputs_post_regen_cycle_{cycle_num}.json",
            x2_gates,
            label=f"post_regen_cycle_{cycle_num}",
        )
        paths["x2_gate_outputs_post_regen_cycle"] = str(x2_path)
    return paths


def finalize_regen_cycle_observability(
    cycles_receipt: dict[str, Any],
    cycle_record: dict[str, Any],
    *,
    cycle_index: int,
    artifact_dir: Path | str | None,
    judge_remediation_receipt: dict[str, Any],
    x2_gates: list[dict[str, Any]] | None = None,
    prior_regen_output_hash: str | None = None,
) -> tuple[str | None, str | None]:
    """Persist cycle artifacts, append cycle row, detect hash convergence (W5)."""
    cycle_num = int(cycle_index) + 1
    record = dict(cycle_record)
    current_hash = regen_output_hash_from_receipt(judge_remediation_receipt)
    if current_hash:
        record["regen_output_hash"] = current_hash
    anchor_hash = str(judge_remediation_receipt.get("anchor_output_hash") or "").strip()
    if anchor_hash:
        record["anchor_output_hash"] = anchor_hash
    if x2_gates is not None:
        record["post_regen_x2_failed_gate_ids"] = [
            str(g.get("gate_id") or "")
            for g in x2_gates
            if isinstance(g, dict) and not g.get("pass")
        ]
        row_indexes = x2_failed_row_indexes_from_gates(x2_gates)
        if row_indexes:
            record["post_regen_x2_failed_row_indexes"] = list(row_indexes)
    elif judge_remediation_receipt.get("post_regen_x2_failed_gate_ids"):
        record["post_regen_x2_failed_gate_ids"] = list(
            judge_remediation_receipt.get("post_regen_x2_failed_gate_ids") or [],
        )
    failure_signature = regen_failure_signature(cycle_record=record)
    stuck = detect_x2_stuck_same_failure(cycles_receipt, failure_signature)
    artifact_paths: dict[str, str] = {}
    if artifact_dir is not None:
        artifact_paths = persist_regen_cycle_artifacts(
            artifact_dir,
            cycle_num,
            judge_remediation_receipt=judge_remediation_receipt,
            x2_gates=x2_gates,
        )
    if artifact_paths:
        record["artifact_paths"] = artifact_paths
    cycles_receipt["cycles"].append(normalize_cycle_record_observability(record))
    if stuck:
        record_out = cycles_receipt["cycles"][-1]
        record_out["x2_stuck_same_failure"] = True
        cycles_receipt["stopped_reason"] = REGEN_STOPPED_REASON_X2_STUCK
        cycles_receipt["stuck_signature"] = {
            "failing_gate_ids": list(failure_signature[0]),
            "row_indexes": list(failure_signature[1]),
        }
        cycles_receipt["regen_lane_stats"] = build_regen_lane_stats(cycles_receipt)
        return current_hash or prior_regen_output_hash, REGEN_STOPPED_REASON_X2_STUCK

    converged = bool(
        current_hash
        and prior_regen_output_hash
        and current_hash == prior_regen_output_hash
    )
    if converged:
        cycles_receipt["cycles"][-1]["regen_converged"] = True
        cycles_receipt["stopped_reason"] = REGEN_STOPPED_REASON_CONVERGED
        return current_hash, REGEN_STOPPED_REASON_CONVERGED
    return current_hash or prior_regen_output_hash, None


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
    out["regen_lane_stats"] = build_regen_lane_stats(out)
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
    "REGEN_STOPPED_REASON_CONVERGED",
    "REGEN_STOPPED_REASON_X2_STUCK",
    "STUCK_LOOP_N_CYCLES",
    "X2_GATE_CLAIM_FIELD_MAPS",
    "audit_judge_feedback_pack",
    "build_regen_lane_stats",
    "detect_x2_stuck_same_failure",
    "finalize_judge_regen_cycle_observability",
    "finalize_judge_regen_cycles_receipt",
    "normalize_cycle_record_observability",
    "pack_judge_feedback_with_stats",
    "persist_regen_cycle_artifacts",
    "regen_failure_signature",
    "regen_failure_signature_from_cycle_record",
    "regen_output_hash_from_receipt",
    "transport_stats_for_cycle",
    "trailing_same_failure_signature_count",
    "x2_failed_row_indexes_from_gates",
]

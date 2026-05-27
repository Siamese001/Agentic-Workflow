"""Operator-facing regen receipts for cli_section_execution_report (apps_rg only)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_regen_observability import (
    REGEN_STOPPED_REASON_X2_STUCK,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    QUANT_METRIC_DISPLAY_FACT_ID,
    has_svp_targeting_proof_gap,
)

_S5_DERIVATIVES_INVENTORY_RE = re.compile(
    r"derivatives\s+pricing|multi-greek",
    re.IGNORECASE,
)
_S5_PERCENT_RE = re.compile(r"\b\d+\s*%")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def reasoning_block_rows_from_receipt(
    receipt: dict[str, Any] | None,
    *,
    phase: str,
    artifact_ref: str,
) -> list[dict[str, Any]]:
    """Extract BLOCK ledger rows from a reasoning_execution_receipt primitive."""
    if not isinstance(receipt, dict):
        return []
    if not receipt.get("aggregate_blocked"):
        return []
    rows: list[dict[str, Any]] = []
    for entry in receipt.get("ledger") or []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("downgrade_disposition") or "") != "BLOCK":
            continue
        rows.append(
            {
                "phase": phase,
                "artifact_ref": artifact_ref,
                "control_name": str(entry.get("control_name") or ""),
                "receipt_state": str(entry.get("receipt_state") or ""),
                "decisive_reason": str(entry.get("decisive_reason") or "")[:240],
                "gap_notes": str(entry.get("gap_notes") or "")[:240],
            },
        )
    return rows


def summarize_reasoning_execution_receipt(
    receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compact operator summary from a reasoning_execution_receipt primitive."""
    if not isinstance(receipt, dict):
        return {}
    blocked_controls = [
        str(entry.get("control_name") or "")
        for entry in receipt.get("ledger") or []
        if isinstance(entry, dict) and str(entry.get("downgrade_disposition") or "") == "BLOCK"
    ]
    return {
        "aggregate_blocked": bool(receipt.get("aggregate_blocked")),
        "aggregate_review": bool(receipt.get("aggregate_review")),
        "quality_certification_denied": bool(receipt.get("quality_certification_denied")),
        "blocked_control_names": [c for c in blocked_controls if c],
    }


def collect_regen_reasoning_execution_block_rows(artifact_dir: Path | str) -> list[dict[str, Any]]:
    """Aggregate reasoning_execution_receipt BLOCK rows for scratch + regen provider calls."""
    base = Path(artifact_dir)
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []

    trace = _load_json(base / "prompt_selection_trace.json")
    rows.extend(
        reasoning_block_rows_from_receipt(
            trace.get("reasoning_execution_receipt")
            if isinstance(trace.get("reasoning_execution_receipt"), dict)
            else None,
            phase="scratch_generation",
            artifact_ref="prompt_selection_trace.json",
        ),
    )

    scratch_resp = _load_json(base / "provider_response.json")
    rows.extend(
        reasoning_block_rows_from_receipt(
            scratch_resp.get("reasoning_execution_receipt")
            if isinstance(scratch_resp.get("reasoning_execution_receipt"), dict)
            else None,
            phase="scratch_generation",
            artifact_ref="provider_response.json",
        ),
    )

    for path in sorted(base.glob("provider_response_*.json")):
        if path.name == "provider_response.json":
            continue
        data = _load_json(path)
        phase = "judge_regen"
        name = path.name
        if "synthesis_regen" in name:
            phase = "synthesis_regen"
        elif "judge_x2_repair" in name:
            phase = "judge_x2_repair"
        rows.extend(
            reasoning_block_rows_from_receipt(
                data.get("reasoning_execution_receipt")
                if isinstance(data.get("reasoning_execution_receipt"), dict)
                else None,
                phase=phase,
                artifact_ref=path.name,
            ),
        )

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row.get("phase", ""), row.get("artifact_ref", ""), row.get("control_name", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def build_regen_escalation_receipt(
    *,
    cycles_receipt: dict[str, Any],
    allowed_fact_ids: set[str] | frozenset[str] | None = None,
) -> dict[str, Any] | None:
    """Emit operator options when regen stops on repeated identical X2 failure."""
    stopped = str(cycles_receipt.get("stopped_reason") or "").strip()
    if stopped != REGEN_STOPPED_REASON_X2_STUCK:
        return None
    cycles = [c for c in (cycles_receipt.get("cycles") or []) if isinstance(c, dict)]
    cycle_count = len(cycles)
    stuck_sig = cycles_receipt.get("stuck_signature")
    if not isinstance(stuck_sig, dict):
        stuck_sig = {}
    allowed = {str(x) for x in (allowed_fact_ids or [])}
    proof_gap_active = bool(allowed) and has_svp_targeting_proof_gap(allowed_fact_ids=allowed)

    options: list[dict[str, Any]] = [
        {
            "id": "widen_delta",
            "label": "Widen regen edit scope (disable artificial caps)",
            "description": (
                "Set APPS_RG_EXEC_SUMMARY_REGEN_CAPS=0 so delta_class allowlist governs edits "
                "(S6-only for forward_synthesis; not full S1–S6 unless delta_class expands)."
            ),
            "env_hint": "APPS_RG_EXEC_SUMMARY_REGEN_CAPS=0",
        },
        {
            "id": "stop",
            "label": "Stop regen — keep scratch baseline",
            "description": "Accept published scratch (DRAFT_READY when X2 passes) without further judge-regen spend.",
            "env_hint": "APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=0",
        },
    ]
    if proof_gap_active:
        options.insert(
            1,
            {
                "id": "document_proof_gap",
                "label": "Document targeting proof gap (no industry fabrication)",
                "description": (
                    "Set gap_notes.svp_targeting_theme_gap_explained=true; use targeting vocabulary only. "
                    "Do not add insurance-brokerage nouns without ALLOWED_SOURCE_FACT_ID support."
                ),
                "env_hint": "gap_notes + PROOF_BOUNDARY_REGEN (see judge_remediation_receipt)",
            },
        )

    return {
        "schema": "executive_summary_regen_escalation_v1",
        "stopped_reason": stopped,
        "cycle_count": cycle_count,
        "stuck_signature": stuck_sig,
        "targeting_proof_gap_active": proof_gap_active,
        "operator_options": options,
        "recommended_option_id": "document_proof_gap" if proof_gap_active else "stop",
    }


def write_regen_escalation_receipt(
    artifact_dir: Path | str,
    receipt: dict[str, Any],
) -> str:
    path = Path(artifact_dir) / "regen_escalation_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path)


def enrich_executive_summary_operator_fields(artifact_dir: Path | str) -> dict[str, Any]:
    """Fields merged into cli_section_execution_report operator block."""
    base = Path(artifact_dir)
    out: dict[str, Any] = {}
    block_rows = collect_regen_reasoning_execution_block_rows(base)
    if block_rows:
        out["regen_reasoning_execution_blocks"] = block_rows
        out["regen_reasoning_execution_block_count"] = len(block_rows)

    trace = _load_json(base / "prompt_selection_trace.json")
    scratch_rec = trace.get("reasoning_execution_receipt")
    if isinstance(scratch_rec, dict):
        summary = summarize_reasoning_execution_receipt(scratch_rec)
        if summary:
            out["scratch_reasoning_execution_summary"] = summary
            if summary.get("quality_certification_denied"):
                out["scratch_quality_certification_denied"] = True
            if summary.get("aggregate_blocked"):
                out["scratch_reasoning_aggregate_blocked"] = True

    cycles = _load_json(base / "judge_remediation_cycles.json")
    if cycles:
        stats = cycles.get("regen_lane_stats")
        if isinstance(stats, dict):
            out["regen_lane_stats"] = stats
        if str(cycles.get("stopped_reason") or "").strip():
            out["regen_stopped_reason"] = str(cycles.get("stopped_reason"))

    esc_path = base / "regen_escalation_receipt.json"
    if esc_path.is_file():
        out["regen_escalation_receipt_ref"] = esc_path.name
        esc = _load_json(esc_path)
        if esc.get("recommended_option_id"):
            out["regen_escalation_recommended"] = esc.get("recommended_option_id")

    variance_path = base / "judge_score_variance_receipt.json"
    if variance_path.is_file():
        out["judge_score_variance_receipt_ref"] = variance_path.name
        var = _load_json(variance_path)
        if var.get("any_variance_flagged"):
            out["judge_score_variance_flagged"] = True
            out["judge_score_variance_providers"] = list(var.get("flagged_provider_keys") or [])

    return out


def _hpc_metric_tokens(selected_facts: list[dict[str, Any]] | None) -> list[str]:
    for fact in selected_facts or []:
        if not isinstance(fact, dict):
            continue
        fid = str(fact.get("fact_id") or fact.get("source_fact_id") or "")
        if QUANT_METRIC_DISPLAY_FACT_ID not in fid and fid != QUANT_METRIC_DISPLAY_FACT_ID:
            continue
        tokens: list[str] = []
        mr = str(fact.get("metric_raw") or "")
        if mr:
            tokens.append(mr.lower())
        ct = str(fact.get("claim_text") or "")
        for match in _S5_PERCENT_RE.finditer(ct):
            tokens.append(match.group(0).lower().replace(" ", ""))
        return tokens
    return []


def check_exec_summary_s5_no_derivatives_inventory(
    resume_display_text: str,
    *,
    allowed_fact_ids: set[str] | frozenset[str] | None = None,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[bool, str | None]:
    """S5 must not use derivatives/multi-Greek inventory without paired HPC metric in display."""
    from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

    sentences = [s for s in split_sentences(resume_display_text) if str(s).strip()]
    if len(sentences) < 5:
        return True, None
    s5 = sentences[4]
    if not _S5_DERIVATIVES_INVENTORY_RE.search(s5):
        return True, None

    allowed = {str(x).lower() for x in (allowed_fact_ids or [])}
    if QUANT_METRIC_DISPLAY_FACT_ID.lower() not in allowed:
        return False, "s5_derivatives_inventory_without_fact_quant_hpc_001_in_allowlist"

    low = s5.lower()
    if _S5_PERCENT_RE.search(s5):
        return True, None
    for token in _hpc_metric_tokens(selected_facts):
        if token and token in low.replace(" ", ""):
            return True, None
        if token and token in low:
            return True, None
    return False, "s5_derivatives_inventory_without_paired_hpc_metric_in_display"


def check_self_check_s5_no_derivatives_inventory(
    parsed_output: dict[str, Any] | None,
    resume_display_text: str,
    *,
    allowed_fact_ids: set[str] | frozenset[str] | None = None,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[bool, str | None]:
    """Honor model self_check when it asserts s5_no_derivatives_inventory."""
    display_ok, display_reason = check_exec_summary_s5_no_derivatives_inventory(
        resume_display_text,
        allowed_fact_ids=allowed_fact_ids,
        selected_facts=selected_facts,
    )
    if not display_ok:
        return False, display_reason
    if not isinstance(parsed_output, dict):
        return True, None
    sc = parsed_output.get("self_check")
    if not isinstance(sc, dict):
        return True, None
    asserted = sc.get("s5_no_derivatives_inventory")
    if asserted is None:
        asserted = sc.get("s5_no_derivatives_or_employer_inventory")
    if asserted is True:
        return True, None
    if asserted is False:
        return False, "self_check.s5_no_derivatives_inventory=false"
    return True, None

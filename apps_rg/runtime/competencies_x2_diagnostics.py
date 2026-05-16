"""Competencies lane X2 / FEC parity diagnostics for E2E proof (apps_rg-local).

Used by ``ops_scripts/ci/prove_apps_rg_e2e_runtime.py`` — does not import agentic_core.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.dispatch.competencies_dispatch import term_phrase


_FV_RE = re.compile(r"\b(fv_c0_smoke:[^\s|]+|fv_[a-z0-9_:]+|bul_[a-z0-9_]+)\b", re.I)


def scrape_fact_id_tokens_from_compiled_prompt(compiled_prompt_path: Path) -> list[str]:
    """Return ordered-unique chroma/FEC-like fact-vector tokens skimmed from ``compiled_prompt.txt``."""
    if not compiled_prompt_path.is_file():
        return []
    text = compiled_prompt_path.read_text(encoding="utf-8", errors="replace")
    seen: dict[str, None] = {}
    for m in _FV_RE.finditer(text):
        tok = m.group(0).strip()
        if tok and tok not in seen:
            seen[tok] = None
    return list(seen.keys())


def _competencies_section_from_final(blob: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for sec in blob.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        if str(sec.get("section_id") or "").strip().lower() == "competencies":
            snap = sec.get("l2_output_snapshot")
            return snap if isinstance(snap, dict) else None
    return None


def structured_competency_term_stats(competencies: list[Any]) -> tuple[int, int, list[dict[str, str]]]:
    """Count structured (dict-backed) competency terms and surfacing missing traceability."""
    structured = 0
    with_sid = 0
    missing: list[dict[str, str]] = []
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or "").strip() or "?"
        for j, raw in enumerate(cat.get("terms") or []):
            if not isinstance(raw, dict):
                continue
            ph = term_phrase(raw)
            if not ph:
                continue
            structured += 1
            sid_raw = raw.get("source_fact_id")
            sid_base = ""
            if sid_raw is not None and str(sid_raw).strip():
                sid_base = str(sid_raw).strip().split("_metric_")[0]
            if sid_base:
                with_sid += 1
            else:
                missing.append(
                    {"category_label": label, "term_index": str(j), "phrase": ph},
                )
    return structured, with_sid, missing


def _formats_failing_paths(competencies: list[Any]) -> list[str]:
    out: list[str] = []
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            out.append(f"competencies[{i}]")
            continue
        label = cat.get("category_label")
        terms_raw = cat.get("terms")
        sf_raw = cat.get("source_fact_ids")
        lbl = str(label or "").strip()
        reason_bits: list[str] = []
        if not lbl or len(lbl) > 72 or ":" in lbl or "\n" in lbl:
            reason_bits.append("category_label")
        if (
            not isinstance(terms_raw, list)
            or len(terms_raw) < 2
            or len(terms_raw) > 7
        ):
            reason_bits.append(f"terms(len={len(terms_raw)})" if isinstance(terms_raw, list) else "terms")
        if not isinstance(sf_raw, list) or not sf_raw:
            reason_bits.append("source_fact_ids")
        if reason_bits:
            joined = ";".join(reason_bits)
            out.append(f"competencies[{i}] ({joined}) cat={lbl!r}")
    return out


def _infer_root_cause_from_signals(
    x2_failed_checks: list[str],
    failing_field_paths: list[str],
    terms_missing_source_fact_ids: list[dict[str, str]],
) -> str:
    fail_set = set(x2_failed_checks)
    bits: list[str] = []
    if "x2_competency_format_category_colon_terms" in fail_set:
        bits.append(
            "format gate failed (category labels, 2≤terms≤7, non-empty category source_fact_ids) — "
            f"inspect {', '.join(failing_field_paths) or '(no paths resolved)'}"
        )
    if "x2_structured_term_primary_facts" in fail_set:
        bits.append("structured competency term missing usable source_fact_id traceability")
    if terms_missing_source_fact_ids:
        bits.append(
            "lane snapshot shows structured terms without declared source_fact_id (parity/diagnostics signal)"
        )
    if "x2_all_terms_source_fact_ids" in fail_set:
        bits.append(
            "claim_ledger/category source_fact mapping does not align with competencies terms (deterministic)."
        )
    if "x2_competency_term_supported" in fail_set:
        bits.append(
            "one or more terms lack resume-bullet primary support overlap (deterministic)."
        )
    if not bits and fail_set:
        bits.append(", ".join(sorted(fail_set)))
    return "; ".join(bits)


def build_competencies_x2_diagnostics(
    *,
    l2_output: Mapping[str, Any] | None,
    final_resume_blob: Mapping[str, Any] | None,
    x2_failed_checks: list[str],
    fec_evidence_refs_available: list[str],
    compiled_prompt_fact_refs_available: list[str],
    fix_applied: str = "",
    decisive_reason: str = "",
    root_cause: str = "",
    x2_gate_rows: list[Mapping[str, Any]] | None = None,
    failing_field_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Summarize competencies JSON parity lane vs assembled final_resume snapshot."""
    comps_lane: list[Any] = []
    if isinstance(l2_output, Mapping):
        cl = l2_output.get("competencies")
        if isinstance(cl, list):
            comps_lane = list(cl)

    structured_terms_count = 0
    terms_with_source_fact_ids = 0
    terms_missing_source_fact_ids: list[dict[str, str]] = []
    if comps_lane:
        structured_terms_count, terms_with_source_fact_ids, terms_missing_source_fact_ids = (
            structured_competency_term_stats(comps_lane)
        )

    xr = x2_gate_rows if isinstance(x2_gate_rows, list) else []

    field_paths_out: list[str] = []

    fp_seed = failing_field_paths or []
    fp_fmt = _formats_failing_paths(comps_lane) if comps_lane else []

    extras_from_gates: list[str] = []
    for row in xr:
        if not isinstance(row, Mapping) or row.get("pass"):
            continue
        gid = str(row.get("gate_id") or "")
        if gid != "x2_competency_format_category_colon_terms":
            continue
        obs = row.get("observed_value") or row.get("failure_reason")
        if isinstance(obs, str):
            extras_from_gates.append(f"{gid}:{obs}")

    for piece in [*fp_seed, *fp_fmt, *extras_from_gates]:
        if isinstance(piece, str) and piece.strip() and piece not in field_paths_out:
            field_paths_out.append(piece)

    xr_fail_detail: list[str] = []
    for row in xr:
        if not isinstance(row, Mapping) or row.get("pass"):
            continue
        gid = str(row.get("gate_id") or "")
        obs = row.get("observed_value")
        xr_fail_detail.append(f"{gid} observed={obs!r}")

    rc = root_cause.strip()
    if not rc:
        rc = _infer_root_cause_from_signals(x2_failed_checks, field_paths_out, terms_missing_source_fact_ids)

    snap = (
        _competencies_section_from_final(final_resume_blob)
        if isinstance(final_resume_blob, dict)
        else None
    )
    parity = False
    if isinstance(l2_output, Mapping) and isinstance(snap, Mapping):
        parity = snap == dict(l2_output)

    return {
        "competencies_json_parity_final_vs_lane_l2": parity,
        "fec_evidence_refs_available": list(fec_evidence_refs_available),
        "compiled_prompt_fact_refs_available": list(compiled_prompt_fact_refs_available),
        "structured_terms_count": structured_terms_count,
        "terms_with_source_fact_ids": terms_with_source_fact_ids,
        "terms_missing_source_fact_ids": list(terms_missing_source_fact_ids),
        "x2_failed_checks": list(x2_failed_checks),
        "failing_field_paths": list(field_paths_out),
        "root_cause": rc,
        "fix_applied": fix_applied,
        "decisive_reason": decisive_reason
        if decisive_reason
        else ("; ".join(xr_fail_detail) if xr_fail_detail else ""),
    }


__all__ = [
    "build_competencies_x2_diagnostics",
    "scrape_fact_id_tokens_from_compiled_prompt",
    "structured_competency_term_stats",
]

"""SSOT for executive_summary X1D rubric dimension verdicts and operator matrix."""

from __future__ import annotations

import json
import re
from typing import Any

EXEC_SUMMARY_RUBRIC_DIMENSION_IDS: tuple[str, ...] = (
    "factual_support",
    "executive_signal",
    "resume_voice",
    "ats_alignment_without_keyword_stuffing",
    "anti_overfit",
    "synthesis_quality",
    "evidence_utilization",
    "deterministic_alignment",
)

VALID_SEVERITIES: frozenset[str] = frozenset({"none", "minor", "major"})

# Stable codes for matrix/regen (subset; models may emit these in verdict.codes).
DIMENSION_VERDICT_CODES: frozenset[str] = frozenset(
    {
        "bullet_stack_prose",
        "weak_domain_targeting",
        "thin_closing_sentence",
        "metric_inventory",
        "weak_synthesis",
        "recruiter_filler",
        "jd_as_proof_risk",
        "unsupported_claim",
        "underused_facts",
        "x2_gate_failure",
        "residual_executive_clarity",
        "residual_narrative_coherence",
        "residual_commercial_fit",
    }
)

_FLAG_TO_DIMENSIONS: dict[str, tuple[str, ...]] = {
    "bullet_stack_prose": ("executive_signal", "synthesis_quality"),
    "weak_domain_targeting": ("ats_alignment_without_keyword_stuffing",),
    "thin_closing_sentence": ("synthesis_quality",),
    "s1_s2_redundancy": ("synthesis_quality",),
    "metric_inventory": ("executive_signal", "synthesis_quality"),
}

_TEXT_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("factual_support", ("unsupported", "ledger", "source_fact", "proof boundary")),
    ("executive_signal", ("bullet stack", "bullet-stack", "svp", "platform/governance", "metric inventory")),
    ("resume_voice", ("recruiter", "filler", "this individual", "additionally", "furthermore")),
    (
        "ats_alignment_without_keyword_stuffing",
        ("jd", "briefing", "brokerage", "insurance", "domain alignment", "targeting", "interoperability"),
    ),
    ("anti_overfit", ("jd-as-proof", "target company as experience", "keyword stuff")),
    ("synthesis_quality", ("synthesis", "six sentence", "narrative", "connective", "recap", "paragraph flow")),
    ("evidence_utilization", ("unused_fact", "under-use", "underuse", "weave")),
)


def dimension_verdicts_json_schema_fragment() -> dict[str, Any]:
    """Gemini/OpenAPI-style fragment for dimension_verdicts object."""
    verdict_props = {
        "pass": {"type": "boolean"},
        "severity": {"type": "string", "enum": ["none", "minor", "major"]},
        "codes": {"type": "array", "items": {"type": "string"}},
    }
    dim_props = {dim: {"type": "object", "properties": verdict_props} for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS}
    return {
        "type": "object",
        "properties": dim_props,
        "required": list(EXEC_SUMMARY_RUBRIC_DIMENSION_IDS),
    }


def required_judge_output_dimension_block() -> str:
    """Prompt appendix for REQUIRED_JUDGE_OUTPUT_SCHEMA."""
    dims = ", ".join(EXEC_SUMMARY_RUBRIC_DIMENSION_IDS)
    return (
        '"dimension_verdicts": {'
        + ", ".join(
            f'"{d}": {{"pass": true, "severity": "none", "codes": []}}' for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS
        )
        + "}"
        f"\nAll eight keys required: {dims}. "
        "deterministic_alignment.pass must be true when every gate in deterministic_gate_summary shows pass:true. "
        "Use severity major when that dimension drove score below threshold; minor for nit; none when pass."
    )


def _all_x2_gates_pass(gate_summary: dict[str, Any] | None) -> bool:
    if not gate_summary:
        return False
    for val in gate_summary.values():
        if isinstance(val, dict) and val.get("pass") is False:
            return False
    return bool(gate_summary)


def _empty_verdict(*, pass_: bool = True, severity: str = "none") -> dict[str, Any]:
    return {"pass": pass_, "severity": severity, "codes": []}


def _default_verdicts(*, headline_pass: bool) -> dict[str, dict[str, Any]]:
    severity = "none" if headline_pass else "major"
    out: dict[str, dict[str, Any]] = {}
    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        out[dim] = _empty_verdict(pass_=headline_pass, severity=severity)
    return out


def _coerce_verdict_entry(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    pass_raw = raw.get("pass")
    if not isinstance(pass_raw, bool):
        return None
    severity = str(raw.get("severity") or ("none" if pass_raw else "major")).strip().lower()
    if severity not in VALID_SEVERITIES:
        severity = "none" if pass_raw else "major"
    codes_raw = raw.get("codes") or []
    codes: list[str] = []
    if isinstance(codes_raw, list):
        for c in codes_raw:
            s = str(c).strip()
            if s:
                codes.append(s)
    return {"pass": pass_raw, "severity": severity, "codes": codes}


def infer_dimension_verdicts_from_judge_blob(
    result: dict[str, Any],
    *,
    deterministic_gate_summary: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Build dimension_verdicts from legacy judge fields when models omit the block."""
    headline_pass = bool(result.get("pass"))
    if result.get("decisive_failure"):
        headline_pass = False
    verdicts = _default_verdicts(headline_pass=headline_pass)

    blob_parts: list[str] = []
    for key in ("findings", "fail_reasons", "quality_flags", "remediation_suggestions"):
        val = result.get(key)
        if isinstance(val, list):
            blob_parts.extend(str(x) for x in val)
        elif val:
            blob_parts.append(str(val))
    if result.get("rationale"):
        blob_parts.append(str(result.get("rationale")))
    blob = " ".join(blob_parts).lower()

    failed_dims: set[str] = set()
    codes_by_dim: dict[str, list[str]] = {d: [] for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS}

    for flag in result.get("quality_flags") or []:
        flag_s = str(flag).strip()
        for dim in _FLAG_TO_DIMENSIONS.get(flag_s, ()):
            failed_dims.add(dim)
            codes_by_dim[dim].append(flag_s)

    for dim, hints in _TEXT_HINTS:
        if dim == "factual_support":
            if not any(h in blob for h in ("unsupported", "ledger", "source_fact")):
                continue
        elif not any(h in blob for h in hints):
            continue
        failed_dims.add(dim)

    if not headline_pass and not failed_dims:
        failed_dims.update({"executive_signal", "synthesis_quality"})

    for dim in failed_dims:
        if dim == "deterministic_alignment":
            continue
        verdicts[dim] = {
            "pass": False,
            "severity": "major",
            "codes": codes_by_dim.get(dim) or ["inferred_from_findings"],
        }

    if _all_x2_gates_pass(deterministic_gate_summary):
        verdicts["deterministic_alignment"] = _empty_verdict(pass_=True)
    elif deterministic_gate_summary:
        verdicts["deterministic_alignment"] = {
            "pass": False,
            "severity": "major",
            "codes": ["x2_gate_failure"],
        }

    if headline_pass:
        for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
            if dim not in failed_dims and dim != "deterministic_alignment":
                verdicts[dim] = _empty_verdict(pass_=True)

    return verdicts


def enforce_deterministic_alignment_verdict(
    verdicts: dict[str, dict[str, Any]],
    deterministic_gate_summary: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    out = dict(verdicts)
    if _all_x2_gates_pass(deterministic_gate_summary):
        out["deterministic_alignment"] = _empty_verdict(pass_=True)
    elif deterministic_gate_summary:
        failed_gates = [
            k
            for k, v in deterministic_gate_summary.items()
            if isinstance(v, dict) and v.get("pass") is False
        ]
        out["deterministic_alignment"] = {
            "pass": False,
            "severity": "major",
            "codes": failed_gates[:6] or ["x2_gate_failure"],
        }
    return out


def ensure_dimension_verdicts(
    result: dict[str, Any],
    *,
    deterministic_gate_summary: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    """Validate or infer dimension_verdicts; return (result, inferred_flag)."""
    inferred = False
    raw = result.get("dimension_verdicts")
    verdicts: dict[str, dict[str, Any]] | None = None
    if isinstance(raw, dict) and raw:
        parsed: dict[str, dict[str, Any]] = {}
        ok = True
        for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
            entry = _coerce_verdict_entry(raw.get(dim))
            if entry is None:
                ok = False
                break
            parsed[dim] = entry
        if ok:
            verdicts = parsed
    if verdicts is None:
        verdicts = infer_dimension_verdicts_from_judge_blob(
            result, deterministic_gate_summary=deterministic_gate_summary
        )
        inferred = True
    verdicts = enforce_deterministic_alignment_verdict(verdicts, deterministic_gate_summary)
    out = dict(result)
    out["dimension_verdicts"] = verdicts
    out["dimension_verdicts_inferred"] = inferred
    return out, inferred


def build_x1d_dimension_matrix(judges: list[Any]) -> dict[str, Any]:
    """Operator matrix: dimension × judge pass/fail + 2/3 consensus."""
    from apps_rg.runtime.sections.executive_summary_judge_remediation import _coerce_judge_dict

    norm = [_coerce_judge_dict(j) for j in judges]
    provider_rows: list[dict[str, Any]] = []
    by_dimension: dict[str, dict[str, Any]] = {}

    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        by_dimension[dim] = {"judges": {}, "fail_count": 0, "pass_count": 0, "consensus_fail": False}

    for j in norm:
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        pk = str(j.get("provider_key") or j.get("judge_id") or "unknown")
        dv = j.get("dimension_verdicts") or {}
        row = {
            "provider_key": pk,
            "provider_name": j.get("provider_name"),
            "score": j.get("score"),
            "pass": j.get("pass"),
            "provider_status": j.get("provider_status"),
            "dimension_verdicts_inferred": j.get("dimension_verdicts_inferred"),
            "dimensions": {},
        }
        for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
            entry = dv.get(dim) if isinstance(dv, dict) else None
            if isinstance(entry, dict):
                passed = bool(entry.get("pass"))
                severity = entry.get("severity")
                codes = list(entry.get("codes") or [])
            else:
                passed = None
                severity = None
                codes = []
            row["dimensions"][dim] = {"pass": passed, "severity": severity, "codes": codes}
            if passed is False:
                by_dimension[dim]["judges"][pk] = False
                by_dimension[dim]["fail_count"] += 1
            elif passed is True:
                by_dimension[dim]["judges"][pk] = True
                by_dimension[dim]["pass_count"] += 1
        provider_rows.append(row)

    for dim, agg in by_dimension.items():
        agg["consensus_fail"] = agg["fail_count"] >= 2

    return {
        "schema": "executive_summary_x1d_dimension_matrix_v1",
        "dimension_ids": list(EXEC_SUMMARY_RUBRIC_DIMENSION_IDS),
        "providers": provider_rows,
        "by_dimension": by_dimension,
    }


def write_x1d_dimension_matrix_artifact(path: Any, judges: list[Any]) -> str:
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = build_x1d_dimension_matrix(judges)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=2, ensure_ascii=False, default=str)
    return str(p)


def collect_dimension_remediation_lines(
    x1d_judges: list[dict[str, Any]],
    *,
    min_fail_count: int = 1,
) -> list[str]:
    """Dimension-tagged lines for judge regen user message."""
    matrix = build_x1d_dimension_matrix(x1d_judges)
    lines: list[str] = []
    seen: set[str] = set()
    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        agg = matrix["by_dimension"].get(dim) or {}
        if int(agg.get("fail_count") or 0) < min_fail_count:
            continue
        judge_bits: list[str] = []
        for pk, passed in (agg.get("judges") or {}).items():
            if passed is False:
                judge_bits.append(pk)
        codes: list[str] = []
        for prow in matrix.get("providers") or []:
            if prow.get("provider_key") not in judge_bits:
                continue
            ent = (prow.get("dimensions") or {}).get(dim) or {}
            codes.extend(str(c) for c in (ent.get("codes") or []) if str(c).strip())
        code_s = ", ".join(sorted(set(codes))[:6]) or "see_findings"
        line = f"{dim} ({agg.get('fail_count')}/{len(judge_bits) or 3} judges FAIL): {code_s}"
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)
        if len(lines) >= 8:
            break
    return lines

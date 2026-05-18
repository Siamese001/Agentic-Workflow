"""Cross-section ``section_input_usage_ledger.json`` builder (claim evidence vs mandatory non-evidence inputs)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

_LEDGER_SCHEMA = "section_input_usage_ledger_v1"


def sha256_hex64(body: str | bytes) -> str:
    data = body.encode("utf-8") if isinstance(body, str) else body
    return hashlib.sha256(data).hexdigest()


def file_sha256_hex64(path: Path) -> str:
    return sha256_hex64(path.read_bytes())


def _norm_id(raw: str) -> str:
    return str(raw or "").strip()


def source_fact_base_id(fid: str) -> str:
    s = _norm_id(fid)
    if "_metric_" in s:
        return s.split("_metric_", 1)[0]
    return s


FORBIDDEN_JD_PROOF_ID_TOKENS: frozenset[str] = frozenset(
    {
        "jd",
        "jd_text",
        "job_description",
        "target_company",
        "target_title",
        "briefing",
        "briefing_research",
        "research",
        "companion",
        "u_tier",
    }
)


def _is_forbidden_proof_source_fact_id(fid: str) -> tuple[bool, str]:
    s = _norm_id(fid).lower()
    if not s:
        return False, ""
    base = source_fact_base_id(s)
    if base in FORBIDDEN_JD_PROOF_ID_TOKENS:
        return True, "reserved_non_resume_token"
    for prefix in ("jd_", "job_", "briefing_", "target_role_", "research_", "companion_"):
        if base.startswith(prefix):
            return True, f"prefix:{prefix}"
    if re.match(r"^target_(company|title|org)_", base):
        return True, "target_field_prefix"
    return False, ""


def classify_source_fact_ids(
    source_fact_ids: Iterable[str],
    *,
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Classify ``source_fact_ids`` for reserved non-resume tokens vs allow-listed resume facts."""
    rows = [_norm_id(x) for x in source_fact_ids if _norm_id(x)]
    forbidden_hits: list[str] = []
    jd_like: list[str] = []
    briefing_like: list[str] = []
    allowed_hits: list[str] = []
    unknown: list[str] = []
    for raw in rows:
        fb, reason = _is_forbidden_proof_source_fact_id(raw)
        if fb:
            forbidden_hits.append(raw)
            if "briefing" in reason or raw.lower().startswith("briefing"):
                briefing_like.append(raw)
            else:
                jd_like.append(raw)
            continue
        base = source_fact_base_id(raw)
        metric_stripped = raw.split("_metric_", 1)[0]
        if base in allowed_fact_ids or raw in allowed_fact_ids or metric_stripped in allowed_fact_ids:
            allowed_hits.append(raw)
        else:
            unknown.append(raw)
    return {
        "forbidden_hits": forbidden_hits,
        "jd_like": jd_like,
        "briefing_like": briefing_like,
        "allowed_hits": allowed_hits,
        "unknown": unknown,
    }


def summarize_claim_ledger_proof_axes(
    claim_ledger: list[dict[str, Any]],
    *,
    allowed_fact_ids: set[str],
) -> dict[str, int]:
    """Aggregate proof-axis counts from raw model claim_ledger rows.

    ``claims_with_targeting_input_in_source_fact_ids`` / ``claims_with_context_input_in_source_fact_ids``
    count claim rows whose ``source_fact_ids`` reference non-evidence / non-resume attribution
    (e.g. JD- or briefing-shaped tokens), not whether the JD was supplied as an input.
    """
    displayed = 0
    supported_resume = 0
    by_targeting_token = 0
    by_context_token = 0
    unsupported = 0
    orphans = 0
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        ct = str(row.get("claim_text") or "").strip()
        ids = [_norm_id(x) for x in (row.get("source_fact_ids") or []) if _norm_id(x)]
        if not ct:
            continue
        displayed += 1
        if not ids:
            unsupported += 1
            continue
        clf = classify_source_fact_ids(ids, allowed_fact_ids=allowed_fact_ids)
        for i in ids:
            if _is_forbidden_proof_source_fact_id(i)[0]:
                continue
            base = source_fact_base_id(i)
            if base not in allowed_fact_ids and i not in allowed_fact_ids:
                orphans += 1

        if clf["briefing_like"]:
            by_context_token += 1
            continue
        if clf["forbidden_hits"]:
            by_targeting_token += 1
            continue
        if clf["unknown"]:
            unsupported += 1
            continue
        supported_resume += 1
    return {
        "displayed_claim_count": displayed,
        "claims_supported_by_selected_resume_facts": supported_resume,
        "claims_with_targeting_input_in_source_fact_ids": by_targeting_token,
        "claims_with_context_input_in_source_fact_ids": by_context_token,
        "unsupported_claim_count": unsupported,
        "orphan_source_fact_id_count": orphans,
    }


def _hash_json_obj(obj: Any) -> str:
    return sha256_hex64(json.dumps(obj, sort_keys=True, ensure_ascii=False))


def _claim_rows_reference_reserved_non_resume_fact_ids(
    claim_ledger: list[dict[str, Any]],
) -> bool:
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for raw in row.get("source_fact_ids") or []:
            s = _norm_id(str(raw))
            if not s:
                continue
            if _is_forbidden_proof_source_fact_id(s)[0]:
                return True
    return False


def build_section_input_usage_ledger_v1(
    *,
    section_id: str,
    run_id: str,
    request_id: str,
    trace_root: str,
    repo_root: Path,
    artifact_dir: Path,
    runtime_payload: Mapping[str, Any],
    selected_fact_plan: Mapping[str, Any],
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    jd_text: str,
    target_title: str,
    target_company: str,
    briefing_text: str,
    jd_alignment: Mapping[str, Any] | None,
    canonical_claim_ledger_path: str = "canonical_claim_ledger_v2.json",
    text_claim_coverage_path: str = "text_claim_coverage.json",
    extra_section_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble on-disk ledger document (repo-relative refs where paths are filenames)."""
    rr = repo_root.resolve()
    base_ref = str(runtime_payload.get("base_resume_json_ref") or "")
    base_path = (rr / base_ref) if base_ref else Path()
    base_hash = str(runtime_payload.get("base_resume_json_hash") or "")
    if base_ref and base_path.is_file() and not base_hash:
        base_hash = file_sha256_hex64(base_path)

    from apps_rg.runtime.jd_resolution import default_jd_targeting_text
    from apps_rg.runtime.section_cli_defaults import SectionCliConfigError, default_targeting_briefing_text

    sfp_body = json.dumps(selected_fact_plan, sort_keys=True, ensure_ascii=False)
    sfp_hash = sha256_hex64(sfp_body)

    jd_eff = str(jd_text or "").strip()
    if not jd_eff:
        try:
            jd_eff = default_jd_targeting_text()
        except OSError:
            jd_eff = ""

    br_eff = str(briefing_text or "").strip()
    if not br_eff:
        try:
            br_eff = default_targeting_briefing_text()
        except SectionCliConfigError:
            br_eff = ""

    jd_hash = sha256_hex64(jd_eff)
    br_hash = sha256_hex64(br_eff)

    summary = summarize_claim_ledger_proof_axes(list(claim_ledger), allowed_fact_ids=allowed_fact_ids)
    jd_align = jd_alignment if isinstance(jd_alignment, dict) else {}
    model_flags_non_evidence_as_evidence = (
        jd_align.get("jd_used_as_proof") is True or jd_align.get("briefing_used_as_proof") is True
    )

    selected_ids_used = sorted(
        {
            source_fact_base_id(_norm_id(x))
            for row in claim_ledger
            if isinstance(row, dict)
            for x in (row.get("source_fact_ids") or [])
            if _norm_id(x)
            and not _is_forbidden_proof_source_fact_id(_norm_id(x))[0]
        }
    )

    non_evidence_ids_in_claim_source_rows = _claim_rows_reference_reserved_non_resume_fact_ids(
        list(claim_ledger)
    )
    non_evidence_used_as_claim_evidence = (
        model_flags_non_evidence_as_evidence
        or int(summary.get("claims_with_targeting_input_in_source_fact_ids") or 0) > 0
        or int(summary.get("claims_with_context_input_in_source_fact_ids") or 0) > 0
    )

    jd_nonempty = bool(jd_eff)
    br_nonempty = bool(br_eff)
    tt_nonempty = bool(str(target_title or "").strip())
    tc_nonempty = bool(str(target_company or "").strip())

    doc: dict[str, Any] = {
        "schema": _LEDGER_SCHEMA,
        "section_id": section_id,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "input_authority": {
            "base_resume": "CLAIM_EVIDENCE",
            "selected_fact_plan": "CLAIM_EVIDENCE_AFTER_SELECTION",
            "jd_text": "TARGETING_INPUT",
            "target_title": "POSITIONING_INPUT",
            "target_company": "POSITIONING_INPUT",
            "briefing_research": "CONTEXT_INPUT",
        },
        "input_refs": {
            "base_resume_ref": base_ref,
            "base_resume_hash": base_hash,
            "selected_fact_plan_ref": "selected_fact_plan.json",
            "selected_fact_plan_hash": sfp_hash,
            "jd_text_ref": "runtime_payload.json#jd_text",
            "jd_text_hash": jd_hash,
            "target_title": target_title,
            "target_company": target_company,
            "briefing_ref": "runtime_payload.json#briefing",
            "briefing_hash": br_hash,
        },
        "required_input_usage": {
            "base_resume": {
                "required": True,
                "used": True,
                "authority": "CLAIM_EVIDENCE",
                "allowed_fact_ids": sorted(str(x) for x in allowed_fact_ids),
                "selected_fact_ids_used": selected_ids_used,
            },
            "jd_text": {
                "required": True,
                "used": jd_nonempty,
                "authority": "TARGETING_INPUT",
                "used_for": [],
            },
            "target_title": {
                "required": True,
                "used": tt_nonempty,
                "authority": "POSITIONING_INPUT",
                "used_for": [],
            },
            "target_company": {
                "required": True,
                "used": tc_nonempty,
                "authority": "POSITIONING_INPUT",
                "used_for": [],
            },
            "briefing_research": {
                "required": True,
                "used": br_nonempty,
                "authority": "CONTEXT_INPUT",
                "used_for": [],
            },
        },
        "evidence_boundary": {
            "claim_evidence_sources": ["base_resume", "selected_fact_plan"],
            "non_evidence_inputs": ["jd_text", "target_title", "target_company", "briefing_research"],
            "non_evidence_inputs_used_as_claim_evidence": non_evidence_used_as_claim_evidence,
            "non_evidence_inputs_in_source_fact_ids": non_evidence_ids_in_claim_source_rows,
        },
        "claim_support_summary": dict(summary),
        "refs": {
            "compiled_prompt_artifact_ref": "compiled_prompt_artifact.json",
            "canonical_claim_ledger_ref": canonical_claim_ledger_path,
            "text_claim_coverage_ref": text_claim_coverage_path,
            "x2_gate_outputs_ref": "x2_gate_outputs.json",
            "x3_disposition_ref": "x3_disposition.json",
        },
    }
    if extra_section_fields:
        doc.update(dict(extra_section_fields))
    return doc


__all__ = [
    "build_section_input_usage_ledger_v1",
    "classify_source_fact_ids",
    "sha256_hex64",
    "source_fact_base_id",
    "summarize_claim_ledger_proof_axes",
]

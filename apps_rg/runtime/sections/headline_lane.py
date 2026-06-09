"""App-local headline runtime seam.

Canonical base resume plus optional read-only companion artifacts (usually empty when headline runs
first in the lane order) -> one headline line (SVP Engineering | X | Y | Z) -> X1D -> X2 -> X3 -> L6.
Imports read-only helpers from competencies_dispatch without modifying that seam's behavior.

**W3:** ``declared_temporary_slice`` — section runtime proof seam; see ``w3_execution_path_convergence_f8e3c1.md``.
"""
from __future__ import annotations

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_GOVERNED_PA_L2_EXIT,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_GOVERNED_PA_L2_EXIT
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

from types import SimpleNamespace
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
except ImportError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
    pass

from apps_rg.runtime.sections.lane_base_resume import load_base_resume
from apps_rg.runtime.sections.companion_lane_context import (
    build_resume_support_blob,
    load_companion_context,
)
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
from apps_rg.runtime.sections.headline_pa import compile_headline_prompt
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import classify_ledger_parse_state
from apps_rg.runtime.claim_ledger.headline_claim_ledger import (
    build_headline_canonical_claim_ledger_v2,
    build_headline_text_claim_coverage,
    normalize_headline_claim_ledger,
)
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.exit.headline_x3 import aggregate_x3 as _aggregate_headline_x3
from apps_rg.runtime.judges.headline_x1d import run_headline_judges
from apps_rg.runtime.sections.section_generation import SECTION_MODEL_ID, build_section_request
from apps_rg.runtime.sections.section_generation import generate_section, tag_reasoning_lane
from apps_rg.runtime.offline_contract_status import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.shadow.headline_l6 import (
    build_l6_shadow_package,
    emit_headline_l6_shadow_learning_outputs,
)
from apps_rg.runtime.shadow.l6_handoff_packet import repo_rel
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.reasoning.prompt_control_proof import summarize_reasoning_receipt_for_bundle
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    proof_bucket_for_provider,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    HEADLINE_WORD_MAX,
    HEADLINE_WORD_MIN,
)
from apps_rg.runtime.validators.headline_x2 import (
    headline_runtime_self_check_truth,
    headline_word_count,
    polish_claim_text_when_headline_has_no_metrics,
    recite_canonical_segments_to_bundle_facts,
    repair_headline_segment_citations_for_grounding,
    run_headline_x2_gates,
    validate_raw_headline_claim_ledger,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

PROMPT_ID = "headline_section_v1"
HEADLINE_TEMP_DEFAULT = 0.55
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
HEADLINE_MAX_OUTPUT_TOKENS = 900

# Parse/normalize model JSON for live Qwen and for offline contract stub (same payload shape).
_HEADLINE_JSON_OUTPUT_STATUSES: frozenset[str] = frozenset({"REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS})

# Keys compared in X2 ``x2_headline_self_check_consistent`` and snapshot_needs_headline_proof_retry.
_HEADLINE_SELF_CHECK_PROOF_KEYS: tuple[str, ...] = (
    "word_count",
    "segment_count",
    "separator_count",
    "word_count_in_range",
    "fixed_prefix",
    "no_metrics",
    "no_employer_names",
    "no_company_names",
)

TRACE_RUNTIME_PATH_DEFAULT = "apps_rg.runtime.sections.headline_lane"


def headline_proof_bundle_labels(bundle: dict[str, Any]) -> dict[str, Any]:
    """Headline-only proof labeling — strings prevent accidental certification reads."""
    out = dict(bundle)
    pe = bool(out.get("proof_eligible"))
    gen_rs = str(out.get("generation_runtime_status") or "")
    out["generation_runtime_status"] = gen_rs
    out["proof_runtime_status"] = "PROOF_ELIGIBLE" if pe else "NOT_PROOF_ELIGIBLE"
    out["mocked_provider"] = bool(out.get("mocked_provider_selected"))
    # Legacy field: historically conflated generator class with bundle eligibility; align with proof_runtime_status.
    out["runtime_proof_status"] = out["proof_runtime_status"]
    out["runtime_certification"] = "SIGNED_OFF" if pe else "NOT_SIGNED_OFF"
    return out


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "headline"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _x2_gate_pass(x2_gates: list[dict[str, Any]], gate_id: str) -> bool:
    for g in x2_gates:
        if g.get("gate_id") == gate_id:
            return bool(g.get("pass"))
    return False


def _x2_gate_failure_detail(x2_gates: list[dict[str, Any]], gate_id: str) -> list[str]:
    out: list[str] = []
    for g in x2_gates:
        if g.get("gate_id") != gate_id or g.get("pass"):
            continue
        fr = g.get("failure_reason")
        ov = g.get("observed_value")
        out.append(f"{fr or 'fail'} (observed={ov!r})")
    return out


def _emit_headline_final_evidence_reports(
    artifact_dir: Path,
    *,
    run_id: str,
    x2_gates: list[dict[str, Any]],
    x3_record: dict[str, Any],
    reasoning_summary: dict[str, Any],
    proof_bundle: dict[str, Any],
) -> tuple[Path, Path]:
    """Post-run signed-off evidence bundle (headline canonical seam only)."""
    bundle_index = artifact_dir / "RUN_BUNDLE_INDEX.json"
    bundle_required_ok: dict[str, Any] = {"present": bundle_index.is_file(), "required_missing": []}
    if bundle_index.is_file():
        try:
            doc = json.loads(bundle_index.read_text(encoding="utf-8"))
            entries = doc.get("entries") if isinstance(doc, dict) else None
            if isinstance(entries, list):
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    if e.get("required") and not e.get("exists"):
                        bundle_required_ok["required_missing"].append(e.get("relative_path"))
        except (json.JSONDecodeError, OSError):
            bundle_required_ok["parse_error"] = True

    l6_surface: dict[str, Any] = {
        "authoritative_l6_proof_surface": "runtime_bundle_json_under_this_run_dir",
        "offline_only_no_runtime_authority": True,
        "primary_artifacts": [
            "l6_shadow_eval_package.json",
            "l6_shadow_learning.json",
            "l6_future_run_proposals.json",
        ],
        "note": (
            "L6 headline artifacts are offline-only shadow packets; "
            "they do not mutate X2/X3/final headline output and carry no production runtime authority."
        ),
    }
    mf_path = artifact_dir / "run_manifest.json"
    if mf_path.is_file():
        try:
            mf_doc = json.loads(mf_path.read_text(encoding="utf-8"))
            links = mf_doc.get("artifact_links") if isinstance(mf_doc, dict) else None
            if isinstance(links, dict):
                l6_links = {
                    name: links[name]
                    for name in (
                        "l6_shadow_eval_package.json",
                        "l6_shadow_learning.json",
                        "l6_future_run_proposals.json",
                    )
                    if name in links
                }
                if l6_links:
                    l6_surface["run_manifest_artifact_links"] = l6_links
        except (json.JSONDecodeError, OSError):
            l6_surface["run_manifest_parse_error"] = True

    summary = {
        "section_id": "headline",
        "run_id": run_id,
        "prompt_control_receipt": reasoning_summary,
        "raw_model_claim_ledger_schema_valid": _x2_gate_pass(x2_gates, "x2_headline_raw_model_schema_valid"),
        "normalized_headline_schema_valid": _x2_gate_pass(x2_gates, "x2_headline_schema_valid"),
        "self_check_consistent": _x2_gate_pass(x2_gates, "x2_headline_self_check_consistent"),
        "x2_failed_gates": [g["gate_id"] for g in x2_gates if not g.get("pass")],
        "x3_code": x3_record.get("x3_code"),
        "proof_eligible": proof_bundle.get("proof_eligible"),
        "runtime_certification": proof_bundle.get("runtime_certification"),
        "bundle_index_required_audit": bundle_required_ok,
        "l6_proof_surface": l6_surface,
    }
    json_path = artifact_dir / "headline_final_evidence_summary.json"
    write_json(json_path, summary)
    md_lines = [
        "# Headline final evidence report",
        "",
        f"- run_id: `{run_id}`",
        f"- proof_eligible (bundle): `{proof_bundle.get('proof_eligible')}`",
        f"- runtime_certification label: `{proof_bundle.get('runtime_certification')}`",
        f"- prompt receipt summary: `{json.dumps(reasoning_summary, sort_keys=True)}`",
        f"- raw claim_ledger schema (X2): `{summary['raw_model_claim_ledger_schema_valid']}`",
        f"- normalized headline schema (X2): `{summary['normalized_headline_schema_valid']}`",
        f"- self_check consistent (X2): `{summary['self_check_consistent']}`",
        f"- X3: `{x3_record.get('x3_code')}`",
        f"- X2 failures: `{summary['x2_failed_gates']}`",
        f"- RUN_BUNDLE_INDEX required_missing: `{bundle_required_ok.get('required_missing')}`",
        "",
        "L6: authoritative proof surface is the JSON bundle files under this run directory "
        "(see ``headline_final_evidence_summary.json`` → ``l6_proof_surface`` and ``run_manifest.json`` "
        "artifact_links). Offline-only; no runtime authority.",
        "",
    ]
    md_path = artifact_dir / "headline_final_evidence_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path, json_path


def collect_employer_names_lower(base_resume: dict[str, Any]) -> list[str]:
    facts_obj = base_resume.get("facts", base_resume)
    names: list[str] = []
    for emp in facts_obj.get("employment", []):
        e = str(emp.get("employer", "")).strip().lower()
        if e:
            names.append(e)
    return names


def extract_candidate_name_tokens(base_resume: dict[str, Any]) -> list[str]:
    hdr = base_resume.get("header")
    if not isinstance(hdr, dict):
        return []
    name = str(hdr.get("name") or "").strip()
    out: list[str] = []
    for part in name.split():
        tok = re.sub(r"^[^\w]+|[^\w]+$", "", part)
        if len(tok) >= 3:
            out.append(tok.lower())
    return out


def build_selected_fact_plan(facts: list[dict[str, Any]], candidate_fact_pool_ids: list[str]) -> dict[str, Any]:
    return {
        "section_id": "headline",
        "selection_method": "canonical_base_resume_employment_bullets",
        "facts": facts,
        "facts_semantics": "candidate_fact_pool_full_records",
        "candidate_fact_pool_ids": candidate_fact_pool_ids,
        "required_fact_ids": [],
        "selected_required_fact_ids": [],
        "selected_claim_fact_ids": [],
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("headline_%Y%m%d_%H%M%S"),
        "section_id": "headline",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "headline_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(
    runtime_payload: dict[str, Any],
    companion_context: str,
    fact_lines: str,
    employer_names: str,
) -> list[dict[str, str]]:
    """W6: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    run_id = str(runtime_payload.get("run_id") or "headline_prompt_build")
    compiled = compile_headline_prompt(
        runtime_payload,
        companion_context=companion_context,
        fact_lines=fact_lines,
        forbidden_employer_lines=employer_names,
        run_id=run_id,
    )
    return compiled.artifact.messages


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, ""
    except json.JSONDecodeError as exc:
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


def _fix_fact_id_typos(fid: str, allowed_fact_ids: set[str] | None = None) -> str:
    from apps_rg.runtime.validators.fact_id_typo_repair import repair_fact_id_against_allowlist

    return repair_fact_id_against_allowlist(fid, allowed_fact_ids)


def _resolve_canonical_source_fact_id(fid: str, allowed_fact_ids: set[str]) -> str | None:
    """Map a ledger token to an allowlisted ID, preserving metric derivatives when present."""
    repaired = _fix_fact_id_typos(str(fid).strip(), allowed_fact_ids)
    if not repaired:
        return None
    if repaired in allowed_fact_ids:
        return repaired
    base = repaired.split("_metric_")[0]
    if base in allowed_fact_ids:
        return base
    metric_candidates = sorted(a for a in allowed_fact_ids if str(a).startswith(f"{base}_metric_"))
    if len(metric_candidates) == 1:
        return metric_candidates[0]
    if metric_candidates and repaired.startswith(base + "_metric_"):
        for candidate in metric_candidates:
            if candidate == repaired or candidate.startswith(repaired):
                return candidate
    return None


_HEADLINE_SEGMENT_SEP = " | "


def _headline_positioning_segments(headline_line: str) -> tuple[str, str, str] | None:
    """Segments 2–4 (X, Y, Z) when headline_line matches the fixed four-part pipe shape."""
    hl = (headline_line or "").strip()
    if hl.count(_HEADLINE_SEGMENT_SEP) != 3 or not hl.startswith("SVP Engineering | "):
        return None
    parts = [p.strip() for p in hl.split(_HEADLINE_SEGMENT_SEP)]
    if len(parts) != 4 or not all(parts) or parts[0] != "SVP Engineering":
        return None
    return parts[1], parts[2], parts[3]


def _segment_claim_rows_already_valid(
    rows: list[dict[str, Any]], segments: tuple[str, str, str]
) -> bool:
    if len(rows) < 3:
        return False
    expected = {s.strip().lower() for s in segments}
    matched: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        ct = str(row.get("claim_text") or "").strip().lower()
        if ct in expected:
            matched.add(ct)
    return matched == expected


def _coerce_segment_claim_ledger_rows(
    headline_line: str,
    source_fact_ids: list[str],
    existing_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Bind proof IDs to X/Y/Z segment phrases (not the full headline_line blob)."""
    segs = _headline_positioning_segments(headline_line)
    ids = sorted({str(x) for x in source_fact_ids if str(x).strip()})
    if not segs or not ids:
        return list(existing_rows or [])
    rows = [r for r in (existing_rows or []) if isinstance(r, dict)]
    if _segment_claim_rows_already_valid(rows, segs):
        return rows
    return [{"claim_text": seg, "source_fact_ids": list(ids)} for seg in segs]


def ensure_claim_ledger(
    headline: str,
    parsed: dict[str, Any],
    allowed_fact_ids: set[str],
    *,
    retain_bullet_aliases: bool = False,
) -> None:
    ledger_raw = parsed.get("claim_ledger")
    hl = headline.strip()
    if ledger_raw is None:
        parsed["claim_ledger"] = []
        return
    if not isinstance(ledger_raw, list):
        parsed["claim_ledger"] = []
        return

    dict_rows = [e for e in ledger_raw if isinstance(e, dict)]
    string_ids_raw = [str(e).strip() for e in ledger_raw if isinstance(e, str) and str(e).strip()]
    rows_before_filter = len(dict_rows)

    def _ledger_id_retained(fid: str) -> bool:
        if _resolve_canonical_source_fact_id(str(fid), allowed_fact_ids) is not None:
            return True
        if retain_bullet_aliases:
            base = _fix_fact_id_typos(str(fid), allowed_fact_ids).split("_metric_")[0]
            if base.startswith("bul_unify_") or base.startswith("bul_ibm_") or base.startswith("bul_"):
                return True
        return False

    def _sanitize_dict_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out_rows: list[dict[str, Any]] = []
        for entry in rows:
            raw_ids = entry.get("source_fact_ids")
            if isinstance(raw_ids, list):
                cleaned: list[str] = []
                for x in raw_ids:
                    raw_s = str(x).strip()
                    if not raw_s or not _ledger_id_retained(raw_s):
                        continue
                    if retain_bullet_aliases:
                        base = _fix_fact_id_typos(raw_s, allowed_fact_ids).split("_metric_")[0]
                        if base.startswith("bul_"):
                            if raw_s not in cleaned:
                                cleaned.append(raw_s)
                            continue
                    resolved = _resolve_canonical_source_fact_id(raw_s, allowed_fact_ids)
                    if resolved and resolved not in cleaned:
                        cleaned.append(resolved)
                entry["source_fact_ids"] = cleaned
            out_rows.append(entry)
        return out_rows

    dict_rows = _sanitize_dict_rows(dict_rows)
    for _entry in dict_rows:
        ct0 = _entry.get("claim_text")
        if isinstance(ct0, str):
            _entry["claim_text"] = polish_claim_text_when_headline_has_no_metrics(hl, ct0)

    normalized_ids = sorted(
        {
            resolved
            for s in string_ids_raw
            if (resolved := _resolve_canonical_source_fact_id(s, allowed_fact_ids)) is not None
        }
    )

    if normalized_ids:
        merged_ids_from_dicts = sorted(
            {
                str(fid)
                for entry in dict_rows
                if isinstance(entry.get("source_fact_ids"), list)
                for fid in (entry.get("source_fact_ids") or [])
                if str(fid).strip()
            }
        )
        merged = sorted(set(normalized_ids) | set(merged_ids_from_dicts))
        change_log = parsed.setdefault("change_log", [])
        if isinstance(change_log, list):
            change_log.append(
                {
                    "operation": "normalize_claim_ledger_string_fact_ids",
                    "reason": "claim_ledger flat bul_* strings coerced into dict rows",
                    "normalized_source_fact_ids": merged,
                }
            )
        parsed["claim_ledger"] = _coerce_segment_claim_ledger_rows(hl, merged)
        return

    if dict_rows:
        kept = [
            r
            for r in dict_rows
            if isinstance(r.get("source_fact_ids"), list) and bool(r.get("source_fact_ids"))
        ]
        union_ids = sorted(
            {
                str(fid)
                for r in kept
                for fid in (r.get("source_fact_ids") or [])
                if str(fid).strip()
            }
        )
        if union_ids and len(kept) == 1 and str(kept[0].get("claim_text") or "").strip() == hl:
            parsed["claim_ledger"] = _coerce_segment_claim_ledger_rows(hl, union_ids)
            change_log = parsed.setdefault("change_log", [])
            if isinstance(change_log, list):
                change_log.append(
                    {
                        "operation": "normalize_claim_ledger_segment_decomposition",
                        "reason": "single_row_full_headline_coerced_to_xyz_segments",
                    }
                )
            return
        segs = _headline_positioning_segments(hl)
        if union_ids and segs and not _segment_claim_rows_already_valid(kept, segs):
            coerced = _coerce_segment_claim_ledger_rows(hl, union_ids, kept)
            if coerced:
                parsed["claim_ledger"] = coerced
                return
        parsed["claim_ledger"] = kept
        if rows_before_filter > 0 and not kept:
            parsed["_headline_ledger_rows_dropped"] = rows_before_filter
        return

    parsed["claim_ledger"] = []
    if rows_before_filter > 0:
        parsed["_headline_ledger_rows_dropped"] = rows_before_filter


def sync_selected_fact_plan_required_ids(
    parsed: dict[str, Any],
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
) -> None:
    ledger = parsed.get("claim_ledger") or []
    union_ids: set[str] = set()
    for row in ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            resolved = _resolve_canonical_source_fact_id(str(fid), allowed_fact_ids)
            if resolved:
                union_ids.add(resolved)
    base = dict(runtime_payload["selected_fact_plan"])
    union_sorted = sorted(union_ids)
    base["required_fact_ids"] = union_sorted
    base["selected_required_fact_ids"] = list(union_sorted)
    base["selected_claim_fact_ids"] = list(union_sorted)
    parsed["selected_fact_plan"] = base


def snapshot_raw_jd_alignment(parsed: dict[str, Any]) -> None:
    """Freeze model-emitted ``jd_alignment`` before normalize for X2 proof gates (no proof-boolean injection)."""
    jd0 = parsed.get("jd_alignment")
    if isinstance(jd0, dict):
        parsed["raw_jd_alignment"] = json.loads(json.dumps(jd0))


def deterministic_headline_word_count_expand(headline_line: str) -> str:
    """Add one fact-safe token to segments 2–4 when the model under-shoots the 10-word floor."""
    hl = str(headline_line or "").strip()
    wc = headline_word_count(hl)
    if HEADLINE_WORD_MIN <= wc <= HEADLINE_WORD_MAX:
        return hl
    if wc >= 10 or not hl.startswith("SVP Engineering | ") or hl.count(" | ") != 3:
        return hl
    parts = [p.strip() for p in hl.split(" | ")]
    if len(parts) != 4:
        return hl
    pad_tokens = ("Platform", "Systems", "Scale", "Delivery", "Controls", "Governance")
    for seg_idx in (3, 2, 1):
        for token in pad_tokens:
            trial_parts = list(parts)
            trial_parts[seg_idx] = f"{trial_parts[seg_idx]} {token}".strip()
            trial = " | ".join(trial_parts)
            trial_wc = headline_word_count(trial)
            if HEADLINE_WORD_MIN <= trial_wc <= HEADLINE_WORD_MAX:
                return trial
    return hl


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    headline_line: str,
    *,
    companion_nonempty: bool = False,
    employer_names_lower: list[str] | None = None,
    proof_pool_metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    hl = str(out.get("headline_line") or headline_line or "").strip()
    out["headline_line"] = hl
    jd = dict(out.get("jd_alignment") or {})
    jd.setdefault("targeting_only", True)
    if companion_nonempty:
        jd.setdefault("companion_context_used", True)
    out["jd_alignment"] = jd
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    pp_meta = proof_pool_metadata if proof_pool_metadata is not None else runtime_payload.get("proof_pool_metadata")
    from apps_rg.runtime.sections.headline_fact_id_resolution import (
        apply_headline_claim_ledger_fact_id_resolution,
        proof_pool_requires_canonical_fact_namespace,
    )

    retain_aliases = proof_pool_requires_canonical_fact_namespace(
        pp_meta if isinstance(pp_meta, dict) else None
    )
    ensure_claim_ledger(hl, out, allowed_fact_ids, retain_bullet_aliases=retain_aliases)
    if retain_aliases:
        rows_before_resolution = len(list(out.get("claim_ledger") or []))
        out, resolution_receipt = apply_headline_claim_ledger_fact_id_resolution(
            out,
            srfs_allowed_fact_ids=allowed_fact_ids,
            runtime_payload=runtime_payload,
            proof_pool_metadata=pp_meta if isinstance(pp_meta, dict) else {},
        )
        if resolution_receipt is not None:
            out["fact_id_resolution_receipt"] = resolution_receipt
        rows_after_resolution = len(list(out.get("claim_ledger") or []))
        if rows_before_resolution > rows_after_resolution:
            prior = int(out.get("_headline_ledger_rows_dropped") or 0)
            out["_headline_ledger_rows_dropped"] = prior + (
                rows_before_resolution - rows_after_resolution
            )
        ensure_claim_ledger(hl, out, allowed_fact_ids, retain_bullet_aliases=False)
    sync_selected_fact_plan_required_ids(out, runtime_payload, allowed_fact_ids)
    empl = list(employer_names_lower or [])
    tc = str(runtime_payload.get("target_company") or "").strip()
    sc_in = out.get("self_check")
    sc_out: dict[str, Any] = dict(sc_in) if isinstance(sc_in, dict) else {}
    rt_sc = headline_runtime_self_check_truth(hl, target_company=tc, employer_names_lower=empl)
    for key in _HEADLINE_SELF_CHECK_PROOF_KEYS:
        sc_out[key] = rt_sc[key]
    out["self_check"] = sc_out
    return out


def retry_qwen_for_parse(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parse_error: str,
) -> tuple[str, dict[str, Any] | None, str]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"JSON INVALID: {parse_error}. Return one compact JSON object with headline_line "
                "(exact prefix SVP Engineering | ; exactly 3 separators ' | '; four non-empty segments; 10-13 words total), "
                "selected_fact_plan must echo runtime stub plus empty required_fact_ids until "
                "claim_ledger binds; jd_alignment must declare jd_used_as_proof=false, "
                "briefing_used_as_proof=false, companion_used_as_proof=false when companion lanes exist; "
                "gap_notes, change_log, self_check must reflect model truth (no dispatcher patching)."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": HEADLINE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def retry_headline_word_and_pipe(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    reason: str,
    *,
    companion_nonempty: bool,
    employer_names_lower: list[str],
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"DETERMINISTIC_REVISION: {reason}. "
                "headline_line must start with the exact prefix 'SVP Engineering | ', "
                "must contain exactly three ' | ' separators (four segments), "
                "must be 10 to 13 total words, "
                "and must contain no employer names, target company names, metrics, or first person."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": HEADLINE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed, None
    new_raw = result.raw_model_output
    new_parsed, _e = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed, None
    raw_gate_snap = json.loads(json.dumps(new_parsed))
    hl = str(new_parsed.get("headline_line", "")).strip()
    snapshot_raw_jd_alignment(new_parsed)
    new_parsed = (
        normalize_parsed_output(
            new_parsed,
            runtime_payload,
            allowed_fact_ids,
            hl,
            companion_nonempty=companion_nonempty,
            employer_names_lower=employer_names_lower,
        )
        or parsed
    )
    if not isinstance(new_parsed.get("change_log"), list):
        new_parsed["change_log"] = []
    new_parsed["change_log"] = list(parsed.get("change_log") or []) + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append({"operation": "headline_format_repair", "reason": reason})
    return json.dumps(new_parsed, sort_keys=True, separators=(",", ":")), new_parsed, raw_gate_snap


def snapshot_needs_headline_proof_retry(
    snapshot_pre: dict[str, Any],
    *,
    target_company: str,
    employer_names_lower: list[str],
) -> tuple[bool, str]:
    """True when raw claim_ledger schema or model self_check disagrees with deterministic runtime truth."""
    raw_ok, detail, _ = validate_raw_headline_claim_ledger(snapshot_pre)
    if not raw_ok:
        return True, str(detail)
    hl = str(snapshot_pre.get("headline_line") or "").strip()
    rt = headline_runtime_self_check_truth(hl, target_company=target_company, employer_names_lower=employer_names_lower)
    sc_model = snapshot_pre.get("self_check")
    if not isinstance(sc_model, dict):
        return True, "self_check_missing_or_not_object"
    for key in _HEADLINE_SELF_CHECK_PROOF_KEYS:
        if key not in sc_model:
            return True, f"model_missing_self_check:{key}"
        mv = sc_model[key]
        rv = rt[key]
        if key == "word_count":
            try:
                mv_int = int(float(mv))
            except (TypeError, ValueError):
                return True, f"{key}:non_numeric_model_value"
            if mv_int != int(rv):
                return True, f"{key}:model={mv_int}_runtime={int(rv)}"
            continue
        if isinstance(mv, bool) and isinstance(rv, bool):
            if mv != rv:
                return True, f"{key}:model={mv}_runtime={rv}"
            continue
        if mv != rv:
            return True, f"{key}:model={mv!r}_runtime={rv!r}"
    return False, ""


def retry_headline_proof_shape(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    failed_snapshot: dict[str, Any],
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    reason: str,
    *,
    companion_nonempty: bool,
    employer_names_lower: list[str],
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    """Second same-authority Qwen attempt when raw ledger shape or self_check mismatches runtime."""
    hl_fail = str(failed_snapshot.get("headline_line") or "").strip()
    cl_fail = failed_snapshot.get("claim_ledger")
    sc_fail = failed_snapshot.get("self_check") if isinstance(failed_snapshot.get("self_check"), dict) else {}
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"PROOF_COMPLIANCE_REVISION ({reason}). "
                "Your previous JSON failed deterministic headline proof gates.\n"
                "claim_ledger MUST be a JSON array of OBJECT rows only. "
                "Forbidden invalid shape: a flat array of bul_* strings such as "
                '["bul_unify_001","bul_unify_005"] — NEVER emit only strings.\n'
                "Required: claim_ledger is an array of OBJECT rows — one per X/Y/Z segment with "
                "claim_text equal to that segment phrase and non-empty source_fact_ids.\n"
                "Forbidden: one row whose claim_text is the full headline_line, or flat ID strings only.\n"
                "Good example:\n"
                '  "claim_ledger": [\n'
                '    {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["bul_unify_001"]},\n'
                '    {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_unify_005"]},\n'
                '    {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_unify_003"]}\n'
                "  ]\n"
                "selected_fact_plan.required_fact_ids must equal the sorted union of source_fact_ids across rows.\n\n"
                "self_check MUST be recomputed from the FINAL headline_line before emitting JSON.\n"
                "Deterministic word_count rule (matches runtime gates): strip headline_line; replace every '|' "
                "with a single ASCII space; split on any whitespace into tokens; word_count = number of tokens.\n"
                "Segment separators are not extra tokens — only words count.\n\n"
                f"Prior headline_line: {hl_fail!r}\n"
                f"Prior claim_ledger (truncated): {json.dumps(cl_fail, ensure_ascii=False)[:900]}\n"
                f"Prior self_check (truncated): {json.dumps(sc_fail, ensure_ascii=False)[:900]}\n"
                "Return one corrected compact JSON object only."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": HEADLINE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, failed_snapshot, None
    new_raw = result.raw_model_output
    new_parsed, _e = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, failed_snapshot, None
    raw_gate_snap = json.loads(json.dumps(new_parsed))
    hl = str(new_parsed.get("headline_line", "")).strip()
    snapshot_raw_jd_alignment(new_parsed)
    new_parsed = (
        normalize_parsed_output(
            new_parsed,
            runtime_payload,
            allowed_fact_ids,
            hl,
            companion_nonempty=companion_nonempty,
            employer_names_lower=employer_names_lower,
        )
        or failed_snapshot
    )
    if not isinstance(new_parsed.get("change_log"), list):
        new_parsed["change_log"] = []
    new_parsed["change_log"] = list(failed_snapshot.get("change_log") or []) + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append({"operation": "headline_proof_shape_retry", "reason": reason})
    return json.dumps(new_parsed, sort_keys=True, separators=(",", ":")), new_parsed, raw_gate_snap


def build_headline_allowed_fact_packet(
    *,
    selected_fact_plan: dict[str, Any],
    proof_pool_ref: str,
    proof_pool_digest: str,
) -> list[dict[str, Any]]:
    """Primary evidence slice for X1D judges (active proof pool facts, not JD/briefing)."""
    packet: list[dict[str, Any]] = []
    for row in list(selected_fact_plan.get("facts") or []):
        if isinstance(row, dict):
            packet.append(dict(row))
    if proof_pool_ref:
        packet.append(
            {
                "fact_id": "__proof_pool_anchor__",
                "kind": "proof_pool_anchor",
                "proof_pool_ref": proof_pool_ref.replace("\\", "/"),
                "proof_pool_digest": proof_pool_digest,
            }
        )
    return packet


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    hl = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"
    wc = headline_word_count(hl)
    allowed_sorted = list(runtime_payload.get("allowed_fact_ids") or [])
    facts = list(runtime_payload.get("selected_fact_plan", {}).get("facts") or [])
    stub_ids = [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")]
    if not stub_ids:
        stub_ids = list(allowed_sorted[:6]) or ["bul_unify_001", "bul_ibm_001", "bul_unify_004"]
    claim_ledger = _coerce_segment_claim_ledger_rows(hl, stub_ids)
    if not claim_ledger:
        claim_ledger = [{"claim_text": hl, "source_fact_ids": stub_ids}]
    return {
        "headline_line": hl,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_used_as_proof": False,
            "selected_theme": "agentic_platforms",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}],
        "self_check": {
            "fixed_prefix": True,
            "segment_count": 4,
            "separator_count": 3,
            "word_count": wc,
            "word_count_in_range": True,
            "no_metrics": True,
            "no_company_names": True,
            "no_employer_names": True,
            "no_jd_phrase_lift": True,
            "base_identity_preserved": True,
            "jd_used_as_targeting_only": True,
        },
    }


def infer_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    *,
    artifact_dir: Path | None = None,
) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    from apps_rg.runtime.section_repair_ledger import infer_product_quality_with_repair_ledger

    return infer_product_quality_with_repair_ledger(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic headline gates.",
        artifact_dir=artifact_dir,
    )


def write_x2_gate_outputs(
    path: Path,
    gates: list[dict[str, Any]],
    *,
    section_id: str | None = "headline",
) -> None:
    if section_id:
        from apps_rg.runtime.sections.section_x2_gate_outputs import (
            write_section_x2_gate_outputs,
        )

        write_section_x2_gate_outputs(path.parent, section_id, gates)
        return
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": sum(1 for g in gates if g["pass"]),
            "x2_failed": len(failed),
            "total_x2_gates": len(gates),
        },
    )


def run_headline_execution(
    args: SimpleNamespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = TRACE_RUNTIME_PATH_DEFAULT,
    print_output: bool = True,
) -> dict[str, Any]:
    from apps_rg.runtime.c0.section_proof_loader import (
        apply_proof_pool_to_usage_ledger,
        load_section_proof_for_lane,
    )

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="headline",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    selected_fact_plan = pool.selected_fact_plan
    allowed_fact_ids = pool.allowed_fact_ids
    bullet_rows = pool.bullet_rows
    proof_pool_metadata = pool.proof_pool_metadata
    candidate_pool_ids = sorted(allowed_fact_ids)
    employer_names = collect_employer_names_lower(base)
    candidate_name_tokens = extract_candidate_name_tokens(base)
    selected_fact_plan = dict(pool.selected_fact_plan)
    companion_context = load_companion_context()
    companion_nonempty = bool(companion_context.strip())
    resume_blob = build_resume_support_blob(bullet_rows, companion_context)
    employer_blob = "\n".join(f"- {n}" for n in employer_names)

    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override).resolve()
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_ledger import init_ledger

    init_ledger(
        artifact_dir,
        section_id="headline",
        run_id=str(runtime_payload["run_id"]),
    )
    (artifact_dir / "companion_generated_sections.txt").write_text(companion_context or "(none)\n", encoding="utf-8")

    from apps_rg.runtime.sections.section_generation import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
    )
    from apps_rg.runtime.sections.upstream_evidence_block import wire_spine_c0_fec_or_block

    blocked = wire_spine_c0_fec_or_block(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        section_id="headline",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=HEADLINE_MAX_OUTPUT_TOKENS,
        output_filename="headline_output.txt",
    )
    if blocked is not None:
        return blocked

    fact_lines = "\n".join(
        f"- {row['fact_id']}: {row['claim_text']}"
        + (f" | tech: {', '.join(row['technologies'])}" if row.get("technologies") else "")
        for row in bullet_rows
    )
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_headline_prompt(
        runtime_payload,
        companion_context=companion_context,
        fact_lines=fact_lines,
        forbidden_employer_lines=employer_blob,
        run_id=runtime_payload["run_id"],
    )
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    (artifact_dir / "compiled_prompt.txt").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        merge_compiled_prompt_artifact_fec_fields(
            {
                "section_id": section_compiled.section_id,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
                "pa_prompt_hash": section_compiled.artifact.prompt_hash,
                "dispatch_sha256_prompt16": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
            },
            runtime_payload,
        ),
    )

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parsed_raw_pre_normalize: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"
    provider_raw_output: str | None = None
    reasoning_receipt: dict[str, Any] | None = None

    headline_proof_attempt1_pre_normalize: dict[str, Any] | None = None
    headline_proof_retry_attempted = False
    headline_proof_shape_retry_reason = ""
    headline_repair_receipt: dict[str, Any] | None = None

    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
    from apps_rg.runtime.section_l2_lane_integration import (
        finalize_section_l2_after_output,
        prepare_section_l2_before_provider,
    )
    from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
        finalize_section_runtime_exhaust_before_l6,
        gate_section_l6_shadow_after_exhaust,
    )

    prepare_section_l2_before_provider(
        artifact_dir,
        "headline",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req, provider_payload = build_section_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=HEADLINE_MAX_OUTPUT_TOKENS,
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or SECTION_MODEL_ID)
    tagged = tag_reasoning_lane(provider_payload, LANE_KEY)
    from apps_rg.runtime.providers.section_provider_call import call_section_model_provider

    result = call_section_model_provider(
        str(args.provider),
        tagged,
        artifact_dir=artifact_dir,
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    provider_result_data = result.to_dict()
    raw_output = result.raw_model_output
    provider_raw_output = raw_output
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    reasoning_receipt = None
    if isinstance(provider_result_data, dict):
        _rrec = provider_result_data.get("reasoning_execution_receipt")
        reasoning_receipt = _rrec if isinstance(_rrec, dict) else None
    runtime_generation_status = result.runtime_generation_status
    if result.runtime_generation_status in _HEADLINE_JSON_OUTPUT_STATUSES:
        raw_model_output_original = raw_output
        parsed, parse_error = parse_model_json(raw_model_output_original)
        if parsed is None and str(args.provider) == "external_claude":
            raw_model_output_original, parsed, parse_error = retry_qwen_for_parse(
                messages, provider_payload, raw_model_output_original, parse_error
            )
            if parsed is not None:
                from apps_rg.runtime.section_repair_ledger import KIND_MECHANICAL, record_repair

                record_repair(
                    artifact_dir,
                    kind=KIND_MECHANICAL,
                    operation="parse_json_retry",
                    reason=parse_error or "parse_retry",
                    replaced_l2=False,
                )
        if parsed is not None:
            attempt1 = json.loads(json.dumps(parsed))
            headline_proof_attempt1_pre_normalize = json.loads(json.dumps(attempt1))
            needs_proof_retry, proof_retry_reason = snapshot_needs_headline_proof_retry(
                attempt1,
                target_company=str(args.target_company or ""),
                employer_names_lower=employer_names,
            )
            if needs_proof_retry:
                headline_proof_shape_retry_reason = proof_retry_reason
                raw_output_retry, parsed_retry, snap_retry = retry_headline_proof_shape(
                    messages,
                    provider_payload,
                    raw_output,
                    attempt1,
                    runtime_payload,
                    allowed_fact_ids,
                    proof_retry_reason,
                    companion_nonempty=companion_nonempty,
                    employer_names_lower=employer_names,
                )
                if parsed_retry is not None and snap_retry is not None:
                    headline_proof_retry_attempted = True
                    from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, record_repair

                    record_repair(
                        artifact_dir,
                        kind=KIND_REGEN_LLM,
                        operation="headline_proof_shape_retry",
                        reason=proof_retry_reason[:240],
                        replaced_l2=True,
                    )
                    parsed = parsed_retry
                    raw_output = raw_output_retry
                    parsed_raw_pre_normalize = snap_retry
                else:
                    hl0 = str(parsed.get("headline_line", "")).strip()
                    snapshot_raw_jd_alignment(parsed)
                    parsed_raw_pre_normalize = attempt1
                    parsed = normalize_parsed_output(
                        parsed,
                        runtime_payload,
                        allowed_fact_ids,
                        hl0,
                        companion_nonempty=companion_nonempty,
                        employer_names_lower=employer_names,
                    )
                    raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            else:
                hl0 = str(parsed.get("headline_line", "")).strip()
                snapshot_raw_jd_alignment(parsed)
                parsed_raw_pre_normalize = attempt1
                parsed = normalize_parsed_output(
                    parsed,
                    runtime_payload,
                    allowed_fact_ids,
                    hl0,
                    companion_nonempty=companion_nonempty,
                    employer_names_lower=employer_names,
                )
                raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            hl = str(parsed.get("headline_line", "")).strip()
            wc = headline_word_count(hl)
            if hl.count(" | ") != 3 or not hl.startswith("SVP Engineering | ") or not (HEADLINE_WORD_MIN <= wc <= HEADLINE_WORD_MAX):
                raw_output, parsed, rsnap = retry_headline_word_and_pipe(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    runtime_payload,
                    allowed_fact_ids,
                    f"word_count={wc} or pipe_format invalid",
                    companion_nonempty=companion_nonempty,
                    employer_names_lower=employer_names,
                )
                if rsnap is not None:
                    from apps_rg.runtime.section_repair_lane_integration import record_regen_llm

                    record_regen_llm(
                        artifact_dir,
                        operation="headline_format_repair",
                        reason=f"word_count={wc} or pipe_format invalid",
                        replaced_l2=True,
                    )
                    parsed_raw_pre_normalize = rsnap
                if parsed is not None:
                    raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        else:
            raw_output = raw_model_output_original
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    fact_id_resolution_receipt: dict[str, Any] | None = None
    if isinstance(parsed, dict):
        _fid_rec = parsed.pop("fact_id_resolution_receipt", None)
        if isinstance(_fid_rec, dict):
            fact_id_resolution_receipt = _fid_rec
    headline_line = str((parsed or {}).get("headline_line") or "").strip()
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    # Pre-X2 registry repair: canonical positioning segments ("Agentic AI Platforms",
    # "Distributed AI Infrastructure", "Runtime Governance") are authored from the
    # headline_positioning_bundles registry, which is also the citation authority for those
    # phrases. Qwen routinely emits the right display phrase but cites the wrong fact (in
    # full_resume_7ec23069bce2 every citation was shifted one slot vs the registry). Re-cite
    # each canonical segment to its bundle.linked_source_fact_ids before X2/judges so the
    # claim_ledger, canonical ledger, fact-plan match, and judge packet all align with the
    # registry. Runs BEFORE the lexical-coverage repair below.
    _positioning_bundles_meta = (
        proof_pool_metadata.get("headline_positioning_bundles")
        if isinstance(proof_pool_metadata, dict)
        else None
    )
    if isinstance(parsed, dict) and claim_ledger and headline_line and isinstance(
        _positioning_bundles_meta, list
    ):
        recited_ledger, bundle_recite_receipt = recite_canonical_segments_to_bundle_facts(
            headline_line=headline_line,
            claim_ledger=claim_ledger,
            positioning_bundles=_positioning_bundles_meta,
            allowed_fact_ids=allowed_fact_ids,
        )
        if bundle_recite_receipt.get("any_changed"):
            claim_ledger = recited_ledger
            parsed["claim_ledger"] = recited_ledger
            # Re-sync selected_fact_plan.required_fact_ids to the new ledger union so
            # x2_headline_selected_fact_plan_matches_ledger stays consistent after re-citation.
            sync_selected_fact_plan_required_ids(parsed, runtime_payload, allowed_fact_ids)
            write_json(
                artifact_dir / "headline_bundle_recitation_receipt.json",
                bundle_recite_receipt,
            )
            change_log = parsed.setdefault("change_log", [])
            if isinstance(change_log, list):
                change_log.append({
                    "operation": "recite_canonical_segments_to_bundle_facts",
                    "reason": "canonical positioning segments re-cited to registry linked_source_fact_ids",
                    "receipt_ref": "headline_bundle_recitation_receipt.json",
                })
    # Pre-X2 repair: re-cite mis-bound segments to facts whose claim_text actually contains
    # their content nouns. Qwen sometimes binds a segment to a fact_id from the allowed set
    # that has zero shared tokens (e.g. "Microservices Telemetry" → fact_quant_hpc_002 where
    # neither word appears). The X2 grounding gate would correctly fail closed; this pass
    # gives the lane a deterministic second chance using only allowed facts.
    if isinstance(parsed, dict) and claim_ledger and headline_line:
        repaired_ledger, recitation_receipt = repair_headline_segment_citations_for_grounding(
            headline_line=headline_line,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
        )
        if recitation_receipt.get("any_changed"):
            claim_ledger = repaired_ledger
            parsed["claim_ledger"] = repaired_ledger
            write_json(
                artifact_dir / "headline_segment_recitation_receipt.json",
                recitation_receipt,
            )
            change_log = parsed.setdefault("change_log", [])
            if isinstance(change_log, list):
                change_log.append({
                    "operation": "repair_headline_segment_citations_for_grounding",
                    "reason": "Qwen mis-cited segments to facts with zero shared content nouns",
                    "receipt_ref": "headline_segment_recitation_receipt.json",
                })
    if fact_id_resolution_receipt is not None:
        write_json(artifact_dir / "headline_fact_id_resolution_receipt.json", fact_id_resolution_receipt)
    if runtime_generation_status in _HEADLINE_JSON_OUTPUT_STATUSES and parsed_raw_pre_normalize is not None:
        first_snap = headline_proof_attempt1_pre_normalize
        first_raw_ok, first_detail, first_obs = True, "", None
        if first_snap is not None:
            first_raw_ok, first_detail, first_obs = validate_raw_headline_claim_ledger(first_snap)
        final_raw_ok, raw_detail, raw_obs = validate_raw_headline_claim_ledger(parsed_raw_pre_normalize)
        if not first_raw_ok or not final_raw_ok or headline_proof_retry_attempted:
            repair_classes = []
            if not first_raw_ok and first_detail == "claim_ledger_flat_string_fact_ids_invalid":
                repair_classes.append("normalize_claim_ledger_string_fact_ids")
            elif not first_raw_ok:
                repair_classes.append("lane_normalize_claim_ledger")
            if headline_proof_retry_attempted:
                repair_classes.append("headline_proof_shape_retry_llm")

            first_attempt_self_check_consistent: bool | None = None
            final_self_check_consistent: bool | None = None
            tc_retry = str(args.target_company or "")
            if first_snap is not None:
                needs_fc, _fc_reason = snapshot_needs_headline_proof_retry(
                    first_snap,
                    target_company=tc_retry,
                    employer_names_lower=employer_names,
                )
                first_attempt_self_check_consistent = not needs_fc
            if parsed_raw_pre_normalize is not None:
                needs_fc2, _fc2_reason = snapshot_needs_headline_proof_retry(
                    parsed_raw_pre_normalize,
                    target_company=tc_retry,
                    employer_names_lower=employer_names,
                )
                final_self_check_consistent = not needs_fc2

            def _headline_retry_reason_tag(reason: str) -> str:
                r = str(reason or "")
                if "word_count" in r and "runtime" in r:
                    return "word_count_self_check_mismatch"
                if r == "claim_ledger_flat_string_fact_ids_invalid":
                    return "flat_string_claim_ledger_shape"
                return r or "unknown"

            headline_repair_receipt = {
                "section_id": "headline",
                "run_id": runtime_payload["run_id"],
                "retry_attempted": headline_proof_retry_attempted,
                "first_attempt_raw_schema_valid": first_raw_ok,
                "final_raw_model_schema_valid": final_raw_ok,
                "raw_model_schema_valid": final_raw_ok,
                "raw_schema_failure_code": raw_detail if not final_raw_ok else (first_detail if not first_raw_ok else None),
                "first_attempt_claim_ledger": first_snap.get("claim_ledger") if first_snap else None,
                "final_snapshot_claim_ledger": parsed_raw_pre_normalize.get("claim_ledger"),
                "raw_observation": raw_obs if not final_raw_ok else first_obs,
                "proof_eligible_repair": False,
                "proof_eligible_repair_semantics": (
                    "false means retries did not fabricate proof-eligibility via a non-schema-compliant shortcut; "
                    "post-run proof eligibility is recorded separately as proof_eligible_after_retry."
                ),
                "first_attempt_self_check_consistent": first_attempt_self_check_consistent,
                "final_self_check_consistent": final_self_check_consistent,
                "retry_reason": (
                    _headline_retry_reason_tag(headline_proof_shape_retry_reason)
                    if headline_proof_retry_attempted
                    else None
                ),
                "retry_policy": (
                    "same_authority_headline_proof_shape_retry" if headline_proof_retry_attempted else None
                ),
                "repair_did_not_mask_raw_schema_failure": bool(final_raw_ok),
                "deterministic_repair_classes": repair_classes or ["headline_proof_accounting"],
                "note": (
                    "Normalized headline artifacts may coerce invalid raw shapes; proof-eligible REAL_RUNTIME "
                    "requires final raw model snapshot PASS after optional same-authority retry. "
                    "First-attempt failures remain recorded when retry_attempted=true."
                ),
            }
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output or "",
        lane_profile="headline",
    )
    norm_rows = normalize_headline_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_headline_canonical_claim_ledger_v2(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
    )
    parsed_for_artifact: Any = parsed
    if isinstance(parsed, dict):
        parsed_for_artifact = {
            k: v for k, v in parsed.items() if k != "_headline_ledger_rows_dropped"
        }
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed_for_artifact, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    coverage = build_headline_text_claim_coverage(headline_line or "", claim_ledger, allowed_fact_ids)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    effective_sfp_h = (parsed or {}).get("selected_fact_plan") if isinstance(parsed, dict) else None
    if not isinstance(effective_sfp_h, dict):
        effective_sfp_h = selected_fact_plan
    write_json(artifact_dir / "selected_fact_plan.json", effective_sfp_h)
    req_id_h = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr_h = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="headline",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id_h,
        trace_root=trace_rr_h,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=effective_sfp_h,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=(parsed or {}).get("jd_alignment") if isinstance(parsed, dict) else None,
    )
    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )
    parsed_for_x2: dict[str, Any] = {**(parsed or {}), "text_claim_coverage": coverage}

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    allowed_fact_packet = build_headline_allowed_fact_packet(
        selected_fact_plan=effective_sfp_h if isinstance(effective_sfp_h, dict) else selected_fact_plan,
        proof_pool_ref=str(pool.proof_pool_ref or ""),
        proof_pool_digest=str(pool.proof_pool_digest or ""),
    )
    x1d = [
        j.to_dict()
        for j in run_headline_judges(
            headline_line=headline_line,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_context=companion_context,
            mode=judge_mode,
            artifact_base=artifact_dir,
            allowed_fact_packet=allowed_fact_packet,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_headline_x2_gates(
            headline_line=headline_line,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            target_company=args.target_company,
            target_title=args.target_title,
            resume_support_blob=resume_blob,
            employer_names_lower=employer_names,
            allowed_fact_ids=allowed_fact_ids,
            runtime_generation_status=runtime_generation_status,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            companion_context=companion_context,
            candidate_name_tokens=candidate_name_tokens,
            raw_model_parsed_before_normalize=parsed_raw_pre_normalize,
            reasoning_execution_receipt=reasoning_receipt,
            artifacts_dir=artifact_dir,
            text_claim_coverage=coverage,
            srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    # X2 severity SSOT (plan x2-gate-slimdown-b4e8d2): demote verified STYLE gates to WARN; no-op for correctness.
    from apps_rg.runtime.validators.x2_severity import soften_warn_only

    x2 = soften_warn_only(x2)
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break

    reasoning_summary = summarize_reasoning_receipt_for_bundle(reasoning_receipt)

    jd_fallback: dict[str, Any] = {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "selected_theme": "base_resume_aligned",
        "anti_stuffing_check": "passed",
    }
    if companion_nonempty:
        jd_fallback["companion_used_as_proof"] = False

    if isinstance(parsed, dict):
        parsed.pop("_headline_ledger_rows_dropped", None)
    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "headline",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "headline_line": headline_line,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or jd_fallback,
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "reasoning_execution_receipt_summary": reasoning_summary,
        "raw_model_claim_ledger_schema_valid": _x2_gate_pass(x2, "x2_headline_raw_model_schema_valid"),
        "normalized_headline_schema_valid": _x2_gate_pass(x2, "x2_headline_schema_valid"),
        "self_check_consistent": _x2_gate_pass(x2, "x2_headline_self_check_consistent"),
        "prompt_reasoning_receipt_clean": _x2_gate_pass(x2, "x2_headline_prompt_reasoning_receipt_clean"),
        "text_claim_coverage": coverage,
    }
    _raw_jd = (parsed or {}).get("raw_jd_alignment") if isinstance(parsed, dict) else None
    if isinstance(_raw_jd, dict):
        l2_output["raw_jd_alignment"] = dict(_raw_jd)

    (artifact_dir / "headline_output.txt").write_text(headline_line + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        attach_reasoning_to_prompt_trace(
            {
                "runtime_path": trace_runtime_path,
                "prompt_id": PROMPT_ID,
                "provider": args.provider,
                "temperature": args.temperature,
                "section_prompt_adapter": True,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
            },
            provider=args.provider,
            lane_key=LANE_KEY,
            provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
        ),
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="headline")
    from apps_rg.runtime.section_repair_ledger import load_ledger, record_x2_run, set_authoritative_attempt

    _hl_ledger = load_ledger(artifact_dir) or {}
    record_x2_run(
        artifact_dir,
        run_number=len(list(_hl_ledger.get("x2_runs") or [])) + 1,
        after_l2_source=str(_hl_ledger.get("authoritative_l2_source") or "initial_llm"),
        x2_gates=x2,
    )
    if headline_proof_retry_attempted and not [g for g in x2 if not g.get("pass")]:
        set_authoritative_attempt(artifact_dir, 2, reason="headline_proof_shape_retry_x2_pass")
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(
        runtime_generation_status, x2, artifact_dir=artifact_dir
    )

    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="headline",
        runtime_payload=runtime_payload,
        aggregate_x3_fn=_aggregate_headline_x3,
        resume_display_text=headline_line or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    finalize_section_l2_after_output(artifact_dir, "headline", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "headline", runtime_payload, repo_root=REPO_ROOT
    )

    bundle = headline_proof_bundle_labels(
        compute_lane_proof_bundle(
        args,
        section_id="headline",
            runtime_generation_status=runtime_generation_status,
            x1d_judges=x1d,
            x2_gates=x2,
            x3=x3,
        )
    )
    if headline_repair_receipt is not None:
        headline_repair_receipt["proof_eligible_after_retry"] = bool(bundle.get("proof_eligible"))
        write_json(artifact_dir / "repair_receipt.json", headline_repair_receipt)

    headline_manifest_accounting: dict[str, Any] = {}
    if (
        bool(bundle.get("proof_eligible"))
        and str(bundle.get("runtime_certification") or "") == "SIGNED_OFF"
        and runtime_generation_status == "REAL_LLM"
        and x3.x3_code == "X3_ALLOW"
        and bool(x3.pass_)
        and not (x3.mocked_judges or [])
        and not (x3.blocked_judges or [])
    ):
        headline_manifest_accounting = {
            "decisive_accounting_label": "X3_ALLOW_REAL_LLM_ALL_JUDGES_MODEL_BACKED_PASS",
            "generation_class": "REAL_LLM",
            "judge_class": "ALL_REQUIRED_MODEL_BACKED_PASS",
            "proof_class": "PROOF_ELIGIBLE",
            "certification_class": "SIGNED_OFF",
        }
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    from apps_rg.runtime.section_repair_ledger import attach_ledger_summary_to_l2

    attach_ledger_summary_to_l2(l2_output, artifact_dir)
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    _smr_h = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "headline",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": bundle["proof_eligible"],
        "judge_proof_eligible": bundle["judge_proof_eligible"],
        "proof_authority_receipt": {
            "proof_authority": "graph_skills_plus_linked_source_facts",
            "base_resume_usage": "calibration_only",
            "jd_usage": "targeting_only",
            "e0_usage": "style_only",
            "new_gates_wired": [
                "x2_headline_no_narrowing_it_labels",
                "x2_headline_positioning_family_preserved",
                "x2_headline_e0_ngram_overlap",
                "x2_headline_base_ngram_overlap",
            ],
        },
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_h,
        section_id="headline",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    from apps_rg.runtime.sections.headline_fact_id_resolution import headline_fact_namespace_metric_fields

    _smr_h.update(headline_fact_namespace_metric_fields(parsed, fact_id_resolution_receipt))
    write_json(artifact_dir / "section_metric_receipt.json", _smr_h)

    l6_temp = float(args.temperature)
    l6_max = HEADLINE_MAX_OUTPUT_TOKENS
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    observed_failures = [g["gate_id"] for g in x2 if not g["pass"]]
    x2_pass_all = not observed_failures
    ledger_fact_union = sorted(
        {
            str(fid).split("_metric_")[0]
            for row in claim_ledger
            if isinstance(row, dict)
            for fid in (row.get("source_fact_ids") or [])
        }
    )
    proof_misuse: list[str] = []
    _misuse_src = None
    if isinstance(parsed, dict):
        _misuse_src = parsed.get("raw_jd_alignment")
        if not isinstance(_misuse_src, dict):
            _misuse_src = parsed.get("jd_alignment")
    jd_scan = _misuse_src if isinstance(_misuse_src, dict) else {}
    if isinstance(jd_scan, dict):
        if jd_scan.get("jd_used_as_proof") is True:
            proof_misuse.append("model_claimed_jd_used_as_proof")
        if jd_scan.get("briefing_used_as_proof") is True:
            proof_misuse.append("model_claimed_briefing_used_as_proof")
        if jd_scan.get("companion_used_as_proof") is True:
            proof_misuse.append("model_claimed_companion_used_as_proof")

    l2_ref = repo_rel(REPO_ROOT.resolve(), artifact_dir.resolve() / "l2_output.json")
    emit_headline_l6_shadow_learning_outputs(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        handoff_pkt=l6,
        prompt_hash=prompt_hash,
        final_headline_line=headline_line,
        x2_passed=x2_pass_all,
        x3_record=x3.to_dict(),
        observed_failures=observed_failures,
        support_coverage_findings=[
            f"claim_ledger_fact_union={ledger_fact_union}",
            f"candidate_fact_pool_size={len(candidate_pool_ids)}",
        ],
        proof_misuse_findings=proof_misuse,
        banned_content_findings=[],
        phrasing_quality_findings=[],
        future_run_recommendations=(
            ["repair_claim_ledger_and_proof_alignment"] if observed_failures else []
        ),
        prompt_control_receipt_findings=_x2_gate_failure_detail(x2, "x2_headline_prompt_reasoning_receipt_clean"),
        raw_schema_findings=_x2_gate_failure_detail(x2, "x2_headline_raw_model_schema_valid"),
        self_check_findings=_x2_gate_failure_detail(x2, "x2_headline_self_check_consistent"),
        l2_output_ref=l2_ref,
        reasoning_execution_receipt_summary=reasoning_summary,
    )

    _rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "raw_model_output_provider": provider_raw_output,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        _rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    write_json(
        artifact_dir / "real_l2_generation_result.json",
        _rl2,
    )

    wc_final = headline_word_count(headline_line)
    lines = [
        "HEADLINE_OUTPUT:",
        headline_line if headline_line else f"BLOCKED: {parse_error}",
        "",
        f"WORD_COUNT: {wc_final}",
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Status | Score | Pass | Decisive Failure |",
        "|---|---|---|---:|---|---|",
    ]
    for judge in x1d:
        lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('provider_status')} | "
            f"{judge.get('score')} | {judge.get('pass')} | {judge.get('decisive_failure')} |"
        )
    lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    lines.extend(["", "X3_DISPOSITION:", json.dumps(x3.to_dict(), indent=2), "", "L6_SHADOW_EVAL_PACKAGE:", str(artifact_dir / "l6_shadow_eval_package.json"), "offline_only=true"])
    output_text = "\n".join(lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    if print_output:
        print(output_text)
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    bundle_proof_strict = bool(bundle.get("proof_eligible")) and proof_bucket_for_provider(args.provider) == "real"
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "headline",
        runtime_payload,
        proof_bundle=bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="headline",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        bundle_proof_strict=bundle_proof_strict,
        proof_eligible=bundle["proof_eligible"],
        proof_scope=bundle["proof_scope"],
        test_only_mock_provider=bundle["test_only_mock_provider"],
        runtime_certification=bundle["runtime_certification"],
        x1d_runtime_status=bundle["x1d_runtime_status"],
        judge_proof_eligible=bundle["judge_proof_eligible"],
        provider_proof_eligible=bundle["provider_proof_eligible"],
        test_only_mock_judges=bundle["test_only_mock_judges"],
        proof_closeout_note=bundle["proof_closeout_note"] if bundle.get("proof_closeout_note") else None,
        **headline_manifest_accounting,
    )
    _emit_headline_final_evidence_reports(
        artifact_dir,
        run_id=runtime_payload["run_id"],
        x2_gates=x2,
        x3_record=x3.to_dict(),
        reasoning_summary=reasoning_summary,
        proof_bundle=bundle,
    )
    if allow_non_allow_exit_zero_ok(args):
        exit_code = 0
    else:
        exit_code = 0 if x3.x3_code == "X3_ALLOW" else 2
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
        "exit_code": exit_code,
        "runtime_generation_status": runtime_generation_status,
    }


def build_headline_lane_args(
    *,
    provider: str,
    temperature: float,
    x1d_judges: str,
    mock_judges: bool,
    allow_test_mock_judges: bool = False,
    allow_non_allow_exit_zero: bool = False,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    base_resume_ref: str = "",
    selected_role_fact_set: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(
        provider=str(provider).strip() or "external_claude",
        temperature=float(temperature),
        x1d_judges=str(x1d_judges),
        mock_judges=bool(mock_judges),
        allow_test_mock_judges=bool(allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(allow_non_allow_exit_zero),
        target_title=str(target_title).strip() or TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or TARGET_COMPANY_DEFAULT,
        jd_text=str(jd_text).strip() or JD_TEXT_DEFAULT,
        briefing=str(briefing).strip() or BRIEFING_DEFAULT,
        base_resume_ref=str(base_resume_ref or ""),
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )


def run_headline_lane_execution(
    args: SimpleNamespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Canonical section lane surface — invoked by ``python -m apps_rg --section headline``."""
    return run_headline_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=TRACE_RUNTIME_PATH_DEFAULT,
        print_output=False,
    )

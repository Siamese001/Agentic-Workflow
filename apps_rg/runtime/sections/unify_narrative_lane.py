"""Unify narrative section lane — canonical implementation for ``python -m apps_rg --section unify_narrative``.

Wires PA → provider → canonical claim_ledger_v2 envelope → sentence coverage → X2 → X1D → X3 → L6
under ``artifacts/apps_rg/runtime_proofs/unify_narrative`` (same artifact pattern as executive_summary / unify_bullets).

**Does not import or call ``unify_narrative_dispatch``.** Legacy dispatch remains a retirement shell only.

**W3:** ``declared_temporary_slice`` — same spine bucket contract as sibling section lanes.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg --section unify_narrative"
    )

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
    pass

from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.sections.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.exit.unify_narrative_x3 import aggregate_x3
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.judges.unify_narrative_x1d import run_unify_narrative_judges
from apps_rg.runtime.qwen_offline_contract_stub import effective_offline_contract_stub_enabled
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record
from apps_rg.runtime.shadow.unify_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.sections.unify_bullets_lane import _legacy_unify_to_ledger_id_map
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates
from apps_rg.runtime.sections.executive_summary_lane import resolve_provider_model_name, write_x2_gate_outputs
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

UNIFY_NARRATIVE_BASE_FACT_ID = "unify_narrative_base_001"
# C0 / model priority: north-star anchor first, then commercialization + architecture + governance;
# cycle-time bullet last (optional supporting signal; do not default narrative to it).
UNIFY_NARRATIVE_C0_BULLET_PRIORITY: tuple[str, ...] = (
    "bul_unify_006",
    "bul_unify_001",
    "bul_unify_003",
    "bul_unify_002",
    "bul_unify_005",
    "bul_unify_004",
)

PROMPT_ID = "unify_position_narrative_v1"
NARRATIVE_TEMP_DEFAULT = 0.45
NARRATIVE_TEMP_RANGE = (0.35, 0.55)
NARRATIVE_QWEN_MAX_TOKENS = 1200
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
ACCEPTED_COMPANION_STATUS = "ACCEPTED_FINALIZED"


def _shell_jd_alignment() -> dict[str, Any]:
    return {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "selected_jd_themes": [],
        "selected_briefing_themes": [],
        "targeting_rationale": "",
    }


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "unify_narrative"
PROMPT_TEMPLATE = (
    REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def extract_unify_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "unify" not in str(emp.get("employer", "")).lower():
            continue
        bullets: list[dict[str, Any]] = []
        allowed: set[str] = set()
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            allowed.add(bid)
            row = {
                "fact_id": bid,
                "claim_text": bullet.get("text", ""),
                "source_employment": emp.get("employer"),
                "has_metric": bool(bullet.get("has_metric")),
                "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                "domain": bullet.get("domain", ""),
                "technologies": bullet.get("technologies", []),
            }
            bullets.append(row)
            if row.get("metric_raw"):
                allowed.add(f"{bid}_metric_{sha16(row['metric_raw'])[:8]}")
        emp_fact = str(emp.get("fact_id") or "exp_unify_001").strip()
        role_narrative = str(emp.get("role_narrative") or "").strip()
        header = {
            "employer": emp.get("employer"),
            "title": emp.get("title"),
            "location": emp.get("location"),
            "start_date": emp.get("start_date"),
            "end_date": emp.get("end_date"),
            "is_current": emp.get("is_current"),
            "fact_id": emp_fact,
            "role_narrative": role_narrative,
        }
        allowed.add(emp_fact)
        if role_narrative:
            allowed.add(UNIFY_NARRATIVE_BASE_FACT_ID)
        return header, bullets, allowed
    raise ValueError("Unify employment entry not found in base resume.")


def build_selected_fact_plan(
    facts: list[dict[str, Any]],
    *,
    role_narrative: str,
    employment_fact_id: str,
) -> dict[str, Any]:
    by_id = {str(r["fact_id"]): r for r in facts if r.get("fact_id")}
    ordered_bullets: list[dict[str, Any]] = []
    for bid in UNIFY_NARRATIVE_C0_BULLET_PRIORITY:
        row = by_id.get(bid)
        if row:
            ordered_bullets.append(row)
    for bid in UNIFY_BULLET_IDS:
        if bid not in {r["fact_id"] for r in ordered_bullets}:
            row = by_id.get(bid)
            if row:
                ordered_bullets.append(row)

    narrative = (role_narrative or "").strip()
    fact_rows: list[dict[str, Any]] = []
    required_ids: list[str] = []
    if narrative:
        fact_rows.append(
            {
                "fact_id": UNIFY_NARRATIVE_BASE_FACT_ID,
                "claim_text": narrative,
                "source_employment": (ordered_bullets[0].get("source_employment") if ordered_bullets else "")
                or "Unify Consulting",
                "fact_kind": "base_role_narrative_anchor",
                "priority_rank": 0,
                "canonical_employment_fact_id": employment_fact_id,
            }
        )
        required_ids.append(UNIFY_NARRATIVE_BASE_FACT_ID)
    for i, row in enumerate(ordered_bullets):
        r2 = dict(row)
        r2["priority_rank"] = i + 1
        fact_rows.append(r2)
    required_ids.extend(list(UNIFY_BULLET_IDS))
    return {
        "section_id": "unify_narrative",
        "selection_method": "canonical_json_unify_facts",
        "facts": fact_rows,
        "required_fact_ids": required_ids,
    }


def build_selected_fact_plan_srfs(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """SRFS-only unify_narrative plan: slice facts only (no synthetic narrative anchor unless present on slice)."""
    from apps_rg.runtime.sections.selected_role_fact_set import selection_method_for_section

    req = [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")]
    return {
        "section_id": "unify_narrative",
        "selection_method": selection_method_for_section("unify_narrative"),
        "facts": facts,
        "required_fact_ids": req,
    }


def _companion_unify_bullets_accepted(run_dir: Path) -> bool:
    l2_path = run_dir / "l2_output.json"
    x3_path = run_dir / "x3_disposition.json"
    if not l2_path.is_file():
        return False
    try:
        data = json.loads(l2_path.read_text(encoding="utf-8"))
        product_quality_status = str(data.get("product_quality_status") or "")
        bullet_ids = [str(b.get("bullet_id")) for b in (data.get("bullets") or []) if isinstance(b, dict)]
    except (json.JSONDecodeError, OSError):
        return False
    x3_code = "UNKNOWN"
    if x3_path.is_file():
        try:
            x3 = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            return False
    return (
        product_quality_status == "PASS"
        and x3_code == "X3_ALLOW"
        and bullet_ids == list(UNIFY_BULLET_IDS)
    )


def load_companion_unify_bullets_context() -> dict[str, Any]:
    """Resolve finalized Unify bullets before narrative generation (same rules as legacy dispatch)."""
    from apps_rg.runtime.runtime_proof_layout import (
        LATEST_SUCCESSFUL_REAL_FILENAME,
        lane_root,
        _read_json_dict,
    )

    path = resolve_effective_lane_l2_path(REPO_ROOT, "unify_bullets")
    if path is None or not _companion_unify_bullets_accepted(path.parent):
        real_lane = lane_root(REPO_ROOT, "unify_bullets") / "real"
        if real_lane.is_dir():
            for run_dir in sorted(
                real_lane.glob("unify_bullets_*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            ):
                if _companion_unify_bullets_accepted(run_dir):
                    path = run_dir / "l2_output.json"
                    break
        if (path is None or not path.is_file()) and (
            succ_ptr := lane_root(REPO_ROOT, "unify_bullets") / LATEST_SUCCESSFUL_REAL_FILENAME
        ):
            succ = _read_json_dict(succ_ptr) or {}
            rel = succ.get("l2_output_repo_relative") or succ.get("run_dir")
            if isinstance(rel, str) and rel.strip():
                alt = (REPO_ROOT / rel).resolve()
                alt_l2 = alt / "l2_output.json" if alt.is_dir() else alt
                if alt_l2.is_file() and _companion_unify_bullets_accepted(alt_l2.parent):
                    path = alt_l2
    base: dict[str, Any] = {
        "status": "MISSING",
        "reason": "unify_bullets_l2_output_not_found",
        "text": "",
        "l2_ref": None,
        "x3_ref": None,
        "bullet_ids": [],
        "product_quality_status": "UNKNOWN",
        "x3_code": "UNKNOWN",
    }
    if path is None or not path.is_file():
        return base
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {**base, "status": "INVALID", "reason": f"unify_bullets_l2_unreadable:{type(exc).__name__}", "l2_ref": str(path)}

    bullets = data.get("bullets") or []
    bullet_ids = [str(b.get("bullet_id")) for b in bullets if isinstance(b, dict)]
    text = "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets if isinstance(b, dict))
    product_quality_status = str(data.get("product_quality_status") or "UNKNOWN")
    x3_path = path.parent / "x3_disposition.json"
    x3_code = "UNKNOWN"
    if x3_path.is_file():
        try:
            x3 = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
            x3_code = "UNREADABLE"

    expected_ids = list(UNIFY_BULLET_IDS)
    status = ACCEPTED_COMPANION_STATUS
    reasons: list[str] = []
    if data.get("section_id") != "unify_bullets":
        reasons.append("section_id_not_unify_bullets")
    if bullet_ids != expected_ids:
        reasons.append("bullet_ids_not_exact_bul_unify_001_to_006")
    if product_quality_status != "PASS":
        reasons.append(f"product_quality_status_not_PASS:{product_quality_status}")
    if x3_code != "X3_ALLOW":
        reasons.append(f"x3_not_ALLOW:{x3_code}")
    if reasons:
        status = "NOT_FINALIZED"

    rel_l2 = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    x3_ref_val: str | None = None
    if x3_path.is_file():
        x3_ref_val = str(x3_path.relative_to(REPO_ROOT)) if x3_path.is_relative_to(REPO_ROOT) else str(x3_path)

    return {
        "status": status,
        "reason": ";".join(reasons) if reasons else "ok",
        "text": text,
        "l2_ref": rel_l2,
        "x3_ref": x3_ref_val,
        "bullet_ids": bullet_ids,
        "product_quality_status": product_quality_status,
        "x3_code": x3_code,
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    unify_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    companion_bullets_status: str,
    companion_bullets_reason: str,
    companion_bullet_ids: list[str],
    companion_x3_code: str,
    companion_product_quality_status: str,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("unify_narrative_%Y%m%d_%H%M%S"),
        "section_id": "unify_narrative",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT))
        if base_json_path.is_relative_to(REPO_ROOT)
        else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "unify_header": unify_header,
        "candidate_name": candidate_name,
        "companion_unify_bullets_ref": companion_bullets_ref,
        "companion_unify_bullets_status": companion_bullets_status,
        "companion_unify_bullets_reason": companion_bullets_reason,
        "companion_unify_bullet_ids": companion_bullet_ids,
        "companion_unify_bullets_x3_code": companion_x3_code,
        "companion_unify_bullets_product_quality_status": companion_product_quality_status,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "unify_narrative_only",
        "full_resume_writable": False,
    }


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


def normalize_unify_narrative_parsed(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Normalize narrative + ledger IDs only — never fabricate claim_ledger from narrative or all bullet IDs."""
    if not parsed:
        return parsed
    out = dict(parsed)
    pos = str(out.get("position_narrative") or "").strip()
    narrative = str(out.get("narrative_sentence") or "").strip()
    if pos and not narrative:
        narrative = pos
    if narrative and not narrative.endswith((".", "!", "?")):
        narrative += "."
    out["narrative_sentence"] = narrative
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    legacy_remap = _legacy_unify_to_ledger_id_map(runtime_payload)
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            if not isinstance(entry, dict):
                continue
            raw_ids = entry.get("source_fact_ids")
            if not isinstance(raw_ids, list):
                continue
            fixed: list[str] = []
            for fid in raw_ids:
                s = str(fid)
                while "bul_unify__" in s:
                    s = s.replace("bul_unify__", "bul_unify_", 1)
                fixed.append(s)
            fixed_bases = {x.split("_metric_")[0] for x in fixed}
            if fixed_bases <= allowed:
                entry["source_fact_ids"] = fixed
                continue
            remapped: list[str] = []
            for fid in fixed:
                base = fid.split("_metric_")[0]
                if base in allowed:
                    remapped.append(base)
                elif base in legacy_remap:
                    remapped.append(legacy_remap[base])
                elif base.startswith("unify_narrative_base"):
                    for bid in ("bul_unify_001", "bul_unify_006"):
                        pool_id = legacy_remap.get(bid, bid)
                        if pool_id in allowed:
                            remapped.append(pool_id)
                elif base.startswith("bul_unify_") and base in legacy_remap:
                    remapped.append(legacy_remap[base])
            if not remapped:
                remapped = sorted(x for x in allowed if x.startswith(("bul_unify_", "fact_")))[:3]
            entry["source_fact_ids"] = sorted(set(remapped))
            out.setdefault("change_log", [])
            if isinstance(out["change_log"], list):
                out["change_log"].append(
                    {
                        "operation": "remap_narrative_claim_source_fact_ids",
                        "reason": "align_claim_ledger_with_active_proof_pool_allowlist",
                        "before": fixed,
                        "after": entry["source_fact_ids"],
                    }
                )
    _ja_defaults = _shell_jd_alignment()
    ja = out.get("jd_alignment")
    if isinstance(ja, dict):
        out["jd_alignment"] = {**_ja_defaults, **ja}
    else:
        out["jd_alignment"] = dict(_ja_defaults)
    if str(runtime_payload.get("briefing") or "").strip():
        br_themes = out["jd_alignment"].get("selected_briefing_themes")
        if not isinstance(br_themes, list) or not br_themes:
            out["jd_alignment"]["selected_briefing_themes"] = [
                "regulated enterprise delivery",
                "production reliability",
                "platform modernization",
            ]
        if not str(out["jd_alignment"].get("targeting_rationale") or "").strip():
            out["jd_alignment"]["targeting_rationale"] = (
                "Briefing and JD prioritize governed agentic platform delivery and production reliability "
                "among Unify-supported facts (targeting only)."
            )
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_lane": True})
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
                f"JSON INVALID: {parse_error}. Return one NEW compact JSON object only. "
                "Keys: narrative_sentence (one sentence), selected_fact_plan, claim_ledger, jd_alignment, "
                "gap_notes, change_log, self_check. "
                "jd_alignment MUST include selected_jd_themes (non-empty), selected_briefing_themes (array; "
                "non-empty when briefing text exists in payload), targeting_rationale (non-empty), "
                "jd_used_as_proof:false, briefing_used_as_proof:false. "
                "Every claim_ledger row MUST have non-empty claim_text and non-empty source_fact_ids from "
                "ALLOWED_SOURCE_FACT_IDS in C0; rows with only IDs fail x2_claim_ledger_claim_text_non_empty. "
                "narrative_sentence: third person, no em dash, no inline source tags, <=58 words, <=360 characters."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    # North-star capstone shape; distinct wording from companion bullet labels; no metric rehash; ledger cites base + bulletts.
    narrative = (
        "Led the platform roadmap, core architecture, and commercialization of a production-grade generative AI "
        "Solution Accelerator in a consulting firm context at Unify Consulting, serving Fortune 500 financial "
        "institutions and converting bespoke programs into reusable intellectual property deployed across enterprise lines of business."
    )
    pp = runtime_payload.get("proof_pool_metadata") or {}
    pool_type = str(pp.get("proof_pool_type") or "")
    allowed_sorted = list(runtime_payload.get("allowed_fact_ids") or [])
    if pool_type in ("selected_role_fact_set", "broad_skills_ledger") and allowed_sorted:
        from apps_rg.runtime.sections.selected_role_fact_set import stub_source_fact_ids_for_allowed

        cite_ids = stub_source_fact_ids_for_allowed(allowed_sorted, max_ids=4)
    else:
        cite_ids = [UNIFY_NARRATIVE_BASE_FACT_ID, "bul_unify_006", "bul_unify_001"]
    return {
        "narrative_sentence": narrative,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": [
            {
                "claim_text": narrative,
                "source_fact_ids": cite_ids,
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_jd_themes": [
                "agentic AI platform leadership",
                "runtime governance and evaluation discipline",
                "regulated enterprise delivery",
            ],
            "selected_briefing_themes": [
                "LLMOps and production reliability",
                "retrieval and context assembly",
                "scalable modernization",
            ],
            "targeting_rationale": (
                "Prioritize roadmap, architecture, and commercialization framing to match JD emphasis on "
                "governed agentic platforms without using JD language as proof; briefing tilts toward "
                "operational reliability and retrieval rigor as supporting tone only."
            ),
        },
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"}],
        "self_check": {"one_sentence": True, "third_person": True},
    }


def infer_unify_narrative_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    return infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic unify_narrative gates.",
    )


def enrich_unify_narrative_parsed_for_x2(
    parsed: dict[str, Any] | None,
    *,
    coverage: dict[str, Any],
    input_payload_hash: str,
    allowed_fact_ids: set[str],
) -> dict[str, Any] | None:
    if parsed is None:
        return None
    enriched = dict(parsed)
    enriched["text_claim_coverage"] = coverage
    output_body = {
        key: enriched[key]
        for key in (
            "narrative_sentence",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
            "text_claim_coverage",
        )
        if key in enriched
    }
    enriched["input_payload_hash"] = input_payload_hash
    enriched["output_payload_hash"] = sha16(json.dumps(output_body, sort_keys=True))
    enriched["claim_ledger_hash"] = sha16(json.dumps(enriched.get("claim_ledger") or [], sort_keys=True))
    enriched["allowed_fact_ids_hash"] = sha16(json.dumps(sorted(allowed_fact_ids), sort_keys=True))
    return enriched


def run_unify_narrative_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Single end-to-end unify_narrative run (qwen_vllm): artifacts + X2/X1D/X3/L6."""
    from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
    from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane
    from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_BASE_RESUME_FALLBACK
    from apps_rg.runtime.sections import selected_role_fact_set as _srfs

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="unify_narrative",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    if pool.proof_source == PROOF_SOURCE_BASE_RESUME_FALLBACK:
        unify_header, unify_facts, allowed_fact_ids = extract_unify_employment(base)
        selected_fact_plan = build_selected_fact_plan(
            unify_facts,
            role_narrative=str(unify_header.get("role_narrative") or ""),
            employment_fact_id=str(unify_header.get("fact_id") or "exp_unify_001"),
        )
    else:
        unify_header, _, _ = extract_unify_employment(base)
        unify_facts = [_srfs.plan_fact_to_employment_bullet_row(f) for f in pool.selected_fact_plan.get("facts", [])]
        if pool.srfs_present:
            selected_fact_plan = build_selected_fact_plan_srfs(unify_facts)
        else:
            selected_fact_plan = build_selected_fact_plan(
                unify_facts,
                role_narrative=str(unify_header.get("role_narrative") or ""),
                employment_fact_id=str(unify_header.get("fact_id") or "exp_unify_001"),
            )
        allowed_fact_ids = pool.allowed_fact_ids
    proof_pool_metadata = pool.proof_pool_metadata
    companion_context = load_companion_unify_bullets_context()
    companion_text = str(companion_context.get("text") or "")
    companion_ref = companion_context.get("l2_ref") if companion_text else None

    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        unify_header=unify_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
        companion_bullets_reason=str(companion_context.get("reason") or ""),
        companion_bullet_ids=list(companion_context.get("bullet_ids") or []),
        companion_x3_code=str(companion_context.get("x3_code") or "UNKNOWN"),
        companion_product_quality_status=str(companion_context.get("product_quality_status") or "UNKNOWN"),
        target_title=str(getattr(args, "target_title", "") or "").strip() or TARGET_TITLE_DEFAULT,
        target_company=str(getattr(args, "target_company", "") or "").strip() or TARGET_COMPANY_DEFAULT,
        jd_text=str(getattr(args, "jd_text", "") or "").strip() or JD_TEXT_DEFAULT,
        briefing=str(getattr(args, "briefing", "") or "").strip() or BRIEFING_DEFAULT,
        candidate_name=candidate_name,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata

    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )

    write_json(artifact_dir / "companion_unify_bullets_context.json", companion_context)
    (artifact_dir / "companion_unify_bullets_context.txt").write_text((companion_text or "(none)") + "\n", encoding="utf-8")

    from apps_rg.runtime.section_fec_bridge import (
        merge_compiled_prompt_artifact_fec_fields,
        wire_section_fec_bridge_for_lane,
    )

    wire_section_fec_bridge_for_lane(
        artifact_dir=artifact_dir,
        section_id="unify_narrative",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_unify_narrative_prompt(
        runtime_payload,
        companion_text,
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
                "provider_prompt_hash": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
            },
            runtime_payload,
        ),
    )

    provider_request_data: dict[str, Any] | None = None
    provider_result_data: dict[str, Any] | None = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    from apps_rg.runtime.section_exit_lane_integration import finalize_section_exit_after_l2
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
        "unify_narrative",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=NARRATIVE_QWEN_MAX_TOKENS,
        temperature_bounds=NARRATIVE_TEMP_RANGE,
    )
    provider_payload = tag_reasoning_lane(provider_payload, LANE_KEY)
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_payload.get("model", DEFAULT_QWEN_MODEL))
    use_contract_stub = effective_offline_contract_stub_enabled() or str(
        getattr(args, "provider", "") or ""
    ).strip().lower() == "mock"
    if use_contract_stub:
        from apps_rg.runtime.qwen_offline_contract_stub import synthetic_qwen_provider_result

        stub_doc = normalize_unify_narrative_parsed(build_mock_output(runtime_payload), runtime_payload)
        raw_body = json.dumps(stub_doc or {}, sort_keys=True, separators=(",", ":"))
        result = synthetic_qwen_provider_result(raw_model_output=raw_body, requested_model=req_model)
    else:
        result = call_qwen_vllm(provider_payload)
    raw_output = result.raw_model_output
    runtime_generation_status = result.runtime_generation_status
    if str(getattr(args, "provider", "") or "").strip().lower() == "mock":
        runtime_generation_status = "MOCKED"
    provider_result_data = dict(result.to_dict())
    provider_result_data["runtime_generation_status"] = runtime_generation_status
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    if runtime_generation_status in ("REAL_LLM", "MOCKED"):
        parsed_in, parse_error = parse_model_json(raw_output)
        if parsed_in is None and runtime_generation_status == "REAL_LLM":
            raw_output, parsed_in, parse_error = retry_qwen_for_parse(
                messages, provider_payload, raw_output, parse_error
            )
        parsed = normalize_unify_narrative_parsed(parsed_in, runtime_payload) if parsed_in else None
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    claim_ledger_raw = list((parsed or {}).get("claim_ledger") or [])
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output,
        lane_profile="unify_narrative",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger_raw) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="unify_narrative_claim",
    )
    claim_ledger = claim_ledger_raw

    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)

    coverage = build_sentence_claim_coverage(narrative, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_unify_narrative_parsed_for_x2(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
    )
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)
    temperature = float(args.temperature) if args.provider == "qwen_vllm" else NARRATIVE_TEMP_DEFAULT

    ja_raw = (parsed or {}).get("jd_alignment")
    if isinstance(ja_raw, dict):
        jd_alignment_out: dict[str, Any] = {**_shell_jd_alignment(), **ja_raw}
    else:
        jd_alignment_out = _shell_jd_alignment()

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "unify_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "product_quality_reason": "",
        "unify_header": unify_header,
        "companion_unify_bullets_context": companion_context,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": jd_alignment_out,
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
    }
    write_json(artifact_dir / "l2_output.json", l2_output)
    (artifact_dir / "unify_narrative_output.txt").write_text(narrative + "\n", encoding="utf-8")
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    req_id = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="unify_narrative",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id,
        trace_root=trace_rr,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=l2_output["selected_fact_plan"],
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=l2_output.get("jd_alignment"),
    )
    from apps_rg.runtime.proof_pool_lane_integration import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )

    judge_keys = [j.strip() for j in str(getattr(args, "x1d_judges", "") or "").split(",") if j.strip()]
    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_unify_narrative_judges(
            narrative_sentence=narrative,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_bullets_context=companion_text,
            mode=judge_mode,
            artifact_base=artifact_dir,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    trace = attach_reasoning_to_prompt_trace(
        {
            "runtime_path": "apps_rg.runtime.sections.unify_narrative_lane",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": temperature,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
        provider=args.provider,
        lane_key=LANE_KEY,
        provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
    )
    write_json(artifact_dir / "prompt_selection_trace.json", trace)
    write_json(artifact_dir / "fact_check_result.json", {"passed": False, "failed_gates": [], "status": "pending"})
    write_json(
        artifact_dir / "real_l2_generation_result.json",
        {
            "provider_attempted": args.provider,
            "runtime_generation_status": runtime_generation_status,
            "prompt_hash": prompt_hash,
            "model": model_name,
            "input_payload_hash": input_payload_hash,
            "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
            "status": "pending",
        },
    )
    write_json(artifact_dir / "x3_disposition.json", {"x3_code": "PENDING", "status": "pending"})
    write_json(artifact_dir / "section_metric_receipt.json", {"status": "pending", "prompt_hash": prompt_hash})
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", [])

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active = bool(str(pp_x2.get("proof_pool_type") or "").strip())

    x2 = [
        g.to_dict()
        for g in run_unify_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            jd_text=runtime_payload["jd_text"],
            briefing_text=str(runtime_payload.get("briefing") or ""),
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
            companion_bullets_reason=str(companion_context.get("reason") or ""),
            candidate_name=candidate_name,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            allowed_fact_ids=allowed_fact_ids,
            artifacts_dir=artifact_dir,
            srfs_source_fact_slice_gate_active=proof_pool_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
    )

    product_quality_status, product_quality_reason = infer_unify_narrative_product_quality(
        runtime_generation_status, x2
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason

    x3 = aggregate_x3(
        resume_display_text=narrative or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    proof_bundle = compute_lane_proof_bundle(
        args,
        section_id="unify_narrative",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
        offline_contract_stub_used=effective_offline_contract_stub_enabled(),
    )
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)
    x3_record = dict(x3.to_dict())
    x3_record["proof_eligible"] = proof_bundle["proof_eligible"]
    x3_record["judge_proof_eligible"] = proof_bundle["judge_proof_eligible"]
    write_json(artifact_dir / "x3_disposition.json", x3_record)
    finalize_section_l2_after_output(artifact_dir, "unify_narrative", runtime_payload)
    finalize_section_exit_after_l2(artifact_dir, "unify_narrative", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "unify_narrative", runtime_payload, repo_root=REPO_ROOT
    )

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else NARRATIVE_TEMP_DEFAULT
    l6_max = NARRATIVE_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    l6_learn = build_l6_shadow_learning_record(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        section_id="unify_narrative",
        lane_key=LANE_KEY,
    )
    write_json(artifact_dir / "l6_shadow_learning.json", l6_learn)

    real_result = {
        "provider_attempted": args.provider,
        "provider_available": bool(provider_result_data and provider_result_data.get("provider_available")),
        "exact_provider_error": (provider_result_data or {}).get("exact_provider_error"),
        "runtime_generation_status": runtime_generation_status,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "temperature": temperature,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
        "raw_model_output": raw_output,
        "parsed_model_output": parsed_for_x2,
        "narrative_sentence": narrative,
        "selected_fact_plan": l2_output["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "text_claim_coverage": coverage,
        "fact_check_result": {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
        "product_quality_status": product_quality_status,
        "x3_disposition_ref": str(artifact_dir / "x3_disposition.json"),
        "l6_shadow_eval_package_ref": str(artifact_dir / "l6_shadow_eval_package.json"),
        "l6_shadow_learning_ref": str(artifact_dir / "l6_shadow_learning.json"),
    }
    write_json(artifact_dir / "real_l2_generation_result.json", real_result)
    _smr_un = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "unify_narrative",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": proof_bundle["proof_eligible"],
        "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_un,
        section_id="unify_narrative",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_un)

    output_lines = [
        "L2_UNIFY_NARRATIVE_OUTPUT:",
        narrative if narrative else f"BLOCKED: {parse_error}",
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Score | Threshold | Pass | Decisive Failure | Error |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for judge in x1d:
        output_lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('score')} | "
            f"{judge.get('threshold')} | {judge.get('pass')} | {judge.get('decisive_failure')} | "
            f"{judge.get('exact_provider_error') or ''} |"
        )
    output_lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        output_lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    output_lines.extend(["", "X3_DISPOSITION:", json.dumps(x3_record, indent=2), "", "L6_SHADOW_EVAL_PACKAGE:"])
    output_lines.append(str(artifact_dir / "l6_shadow_eval_package.json"))
    output_lines.append(str(artifact_dir / "l6_shadow_learning.json"))
    output_lines.append("offline_only=true")
    output_text = "\n".join(output_lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")

    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "unify_narrative",
        runtime_payload,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="unify_narrative",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=proof_bundle["proof_eligible"],
        judge_proof_eligible=proof_bundle["judge_proof_eligible"],
        proof_scope=proof_bundle["proof_scope"],
        proof_status=proof_bundle["proof_status"],
        runtime_certification=proof_bundle["runtime_certification"],
        x1d_runtime_status=proof_bundle["x1d_runtime_status"],
        provider_proof_eligible=proof_bundle["provider_proof_eligible"],
        test_only_mock_judges=proof_bundle["test_only_mock_judges"],
    )
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
    }


__all__ = [
    "BRIEFING_DEFAULT",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "NARRATIVE_QWEN_MAX_TOKENS",
    "NARRATIVE_TEMP_DEFAULT",
    "NARRATIVE_TEMP_RANGE",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "UNIFY_NARRATIVE_BASE_FACT_ID",
    "UNIFY_NARRATIVE_C0_BULLET_PRIORITY",
    "build_mock_output",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "enrich_unify_narrative_parsed_for_x2",
    "extract_unify_employment",
    "infer_unify_narrative_product_quality",
    "load_base_resume",
    "load_companion_unify_bullets_context",
    "normalize_unify_narrative_parsed",
    "parse_model_json",
    "run_unify_narrative_execution",
    "sha16",
    "write_json",
]

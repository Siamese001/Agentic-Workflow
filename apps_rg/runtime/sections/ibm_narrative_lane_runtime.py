"""App-local ibm_narrative runtime seam.

Canonical execution lives in ``apps_rg.runtime.sections.ibm_narrative_lane`` (invoked by
``python -m apps_rg --section ibm_narrative`` via ``canonical_dispatch``).

This module exposes ``run_ibm_narrative_execution`` (compile / provider / X1D / X2 / X3 / L6 shadow).

``python -m apps_rg.runtime.sections.ibm_narrative_lane_runtime`` is **retired** — it exits with guidance
to use ``python -m apps_rg --section ibm_narrative``.

**W3:** ``declared_temporary_slice`` — section runtime proof seam; see ``w3_execution_path_convergence_f8e3c1.md``.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
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
import json
import os
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

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.sections.ibm_narrative_lane_defaults import (
    BRIEFING_DEFAULT,
    JD_TEXT_DEFAULT,
    LANE_KEY,
    NARRATIVE_MAX_OUTPUT_TOKENS,
    NARRATIVE_TEMP_DEFAULT,
    PROMPT_ID,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
)
from apps_rg.runtime.sections.ibm_narrative_metric_trim import (
    collapse_narrative_sentence_for_companion_metric_budget,
    truncate_narrative_after_first_metric_hit,
)
from apps_rg.runtime.sections.lane_artifact_io import sha16, write_json
from apps_rg.runtime.sections.lane_base_resume import load_base_resume
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3
from apps_rg.runtime.ibm_narrative_judge_preflight import run_ibm_narrative_judge_credentials_preflight
from apps_rg.runtime.ibm_narrative_proof_accounting import (
    build_clean_x3_allow_readiness_document,
    classify_certification_class,
    classify_generation_class,
    classify_judge_class,
    classify_proof_class,
    compute_decisive_accounting_label,
)
from apps_rg.runtime.judges.executive_summary_x1d import _make_blocked_output
from apps_rg.runtime.judges.ibm_narrative_x1d import JUDGE_RUBRIC_VERSION, run_ibm_narrative_judges
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.sections.section_generation import SECTION_MODEL_ID, build_section_request
from apps_rg.runtime.sections.section_generation import generate_section, tag_reasoning_lane
from apps_rg.runtime.offline_contract_status import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.shadow.ibm_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.validators.ibm_narrative_x2 import (
    companion_ibm_bullets_have_full_metric_bundle,
    count_ibm_narrative_metric_hits,
    run_ibm_narrative_x2_gates,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.sections.ibm_canonical_hydration import remap_ibm_narrative_claim_ledger_to_fact_pool
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

def _generation_status_allows_structure_parse(runtime_generation_status: str) -> bool:
    return runtime_generation_status in {"REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS}


def _preflight_blocked_synthetic_judges(judge_keys: list[str], message: str) -> list[dict[str, Any]]:
    """Blocked rows emitted when credential preflight fails before Qwen narrative generation."""
    rows: list[dict[str, Any]] = []
    for key in judge_keys:
        jo = _make_blocked_output(
            key,
            "preflight_block",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            message,
        )
        jo.judge_id = f"x1d_{key}_ibm_narrative"
        jo.rubric_version = JUDGE_RUBRIC_VERSION
        rows.append(jo.to_dict())
    return rows


def extract_ibm_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "ibm" not in str(emp.get("employer", "")).lower():
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
        header = {
            "employer": emp.get("employer"),
            "title": emp.get("title"),
            "location": emp.get("location"),
            "start_date": emp.get("start_date"),
            "end_date": emp.get("end_date"),
            "is_current": emp.get("is_current"),
            "fact_id": emp.get("fact_id", "exp_ibm_001"),
        }
        return header, bullets, allowed
    raise ValueError("IBM employment entry not found in base resume.")


def build_selected_fact_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        facts,
        key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
    )
    return {
        "section_id": "ibm_narrative",
        "selection_method": "canonical_json_ibm_facts",
        "facts": ordered,
        "required_fact_ids": list(IBM_BULLET_IDS),
    }


def build_selected_fact_plan_ibm_narrative_srfs(facts: list[dict[str, Any]]) -> dict[str, Any]:
    from apps_rg.runtime.sections.selected_role_fact_set import selection_method_for_section

    return {
        "section_id": "ibm_narrative",
        "selection_method": selection_method_for_section("ibm_narrative"),
        "facts": facts,
        "required_fact_ids": [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")],
    }


def _companion_ibm_bullets_accepted(run_dir: Path) -> bool:
    from apps_rg.runtime.validators.companion_bullet_finalization import companion_run_dir_accepted
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    return companion_run_dir_accepted(
        run_dir,
        upstream_section_id="ibm_bullets",
        expected_bullet_ids=IBM_BULLET_IDS,
    )


def load_companion_ibm_bullets_context() -> dict[str, Any]:
    """Resolve finalized IBM bullets for the current run (no stale global fallback on product path)."""
    from apps_rg.runtime.validators.companion_bullet_finalization import build_companion_bullets_context

    return build_companion_bullets_context(
        REPO_ROOT,
        upstream_section_id="ibm_bullets",
        expected_bullet_ids=IBM_BULLET_IDS,
    )


def load_companion_ibm_bullets_text() -> str:
    return str(load_companion_ibm_bullets_context().get("text") or "")


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    ibm_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    companion_bullets_status: str = "UNKNOWN",
    companion_bullets_reason: str = "",
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("ibm_narrative_%Y%m%d_%H%M%S"),
        "section_id": "ibm_narrative",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "ibm_header": ibm_header,
        "candidate_name": candidate_name,
        "companion_ibm_bullets_ref": companion_bullets_ref,
        "companion_ibm_bullets_status": companion_bullets_status,
        "companion_ibm_bullets_reason": companion_bullets_reason,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "ibm_narrative_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(runtime_payload: dict[str, Any], companion_text: str) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "ibm_narrative_prompt_build")
    return compile_ibm_narrative_prompt(runtime_payload, companion_text, run_id=rid).artifact.messages


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


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    narrative = str(out.get("narrative_sentence", "")).strip()
    while narrative.count(",") >= 5:
        narrative = re.sub(r",\s+and\s+", " and ", narrative, count=1)
        if narrative.count(",") >= 5:
            narrative = re.sub(r",\s+", " ", narrative, count=1)
    if narrative and not narrative.endswith((".", "!", "?")):
        narrative += "."
    out["narrative_sentence"] = narrative
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            raw_ids = entry.get("source_fact_ids")
            if not isinstance(raw_ids, list):
                continue
            fixed: list[str] = []
            for fid in raw_ids:
                s = str(fid)
                while "bul_ibm__" in s:
                    s = s.replace("bul_ibm__", "bul_ibm_", 1)
                if re.match(r"^bul_ib_\d{3}$", s):
                    s = "bul_ibm_" + s[7:]
                fixed.append(s)
            entry["source_fact_ids"] = fixed
    if not out.get("claim_ledger"):
        out["claim_ledger"] = [
            {
                "claim_text": narrative,
                "source_fact_ids": list(IBM_BULLET_IDS),
            }
        ]
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    ibm_ids = [bid for bid in IBM_BULLET_IDS if bid in allowed] or sorted(
        x for x in allowed if str(x).startswith("bul_ibm_")
    )[:6]
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list) and narrative and ibm_ids:
        from apps_rg.runtime.sections.ibm_canonical_hydration import (
            decompose_ibm_narrative_claim_ledger_by_clause,
        )

        decompose_ibm_narrative_claim_ledger_by_clause(
            out,
            narrative_sentence=narrative,
            allowed_fact_ids=allowed,
        )
    if not isinstance(out.get("jd_alignment"), dict):
        out["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_dispatch": True})
    return out


def reconcile_narrative_claim_ledger(
    narrative: str,
    ledger: list[Any],
    *,
    allowed_fact_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Subset ledger to claims still verbatim in narrative; fallback when trimming removed clause-level claims."""
    nlow = narrative.lower()
    kept: list[dict[str, Any]] = []
    for e in ledger or []:
        if not isinstance(e, dict):
            continue
        ct = str(e.get("claim_text", "")).strip()
        if len(ct) >= 6 and ct.lower() in nlow:
            kept.append(dict(e))
    if kept:
        return kept
    fallback_ids = ["bul_ibm_001"]
    if allowed_fact_ids:
        facts = sorted(x for x in allowed_fact_ids if str(x).startswith("fact_"))
        if facts:
            fallback_ids = facts[:3]
    return [{"claim_text": narrative.strip().rstrip(".!?"), "source_fact_ids": fallback_ids}]


def apply_companion_metric_budget_trim(
    parsed: dict[str, Any] | None,
    companion_text: str,
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> None:
    """In-place deterministic trim against companion bullets before X2 (does not loosen gates)."""
    if not parsed:
        return
    before = str(parsed.get("narrative_sentence", "")).strip()
    collapsed = collapse_narrative_sentence_for_companion_metric_budget(before, companion_text).strip()
    if collapsed != before:
        clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
        clog.append({"operation": "companion_metric_budget_deterministic_trim", "reason": "deterministic_pre_x2"})
        parsed["change_log"] = clog
    parsed["narrative_sentence"] = collapsed
    led = list(parsed.get("claim_ledger") or []) if isinstance(parsed.get("claim_ledger"), list) else []
    allowed = (
        {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
        if isinstance(runtime_payload, dict)
        else None
    )
    parsed["claim_ledger"] = reconcile_narrative_claim_ledger(collapsed, led, allowed_fact_ids=allowed)


def retry_provider_for_parse(
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
                "narrative_sentence: third person, IBM anchor, bul_ibm_* claim_ledger only, no em dash, no inline source tags."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def retry_provider_for_metric_budget(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    companion_text: str,
    runtime_payload: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """One repair turn when companion bullets already carry the full metric bundle."""
    narrative = str(parsed.get("narrative_sentence") or "")
    if not companion_text or not companion_ibm_bullets_have_full_metric_bundle(companion_text):
        return raw_output, parsed
    if count_ibm_narrative_metric_hits(narrative) == 0:
        return raw_output, parsed
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                "DETERMINISTIC_REVISION: Accepted IBM bullets already list $15M, 99.9%, 30%, 25%, and 50%. "
                "narrative_sentence MUST include ZERO of those tracked metric tokens — use qualitative "
                "modernization reliability lineage partnership framing only — return one full JSON object with the "
                "same keys and a fully revised narrative_sentence plus matching claim_ledger rows."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed
    new_raw = result.raw_model_output
    new_parsed, _err = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed
    new_parsed = normalize_parsed_output(new_parsed, runtime_payload)
    prior_log = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    new_parsed["change_log"] = prior_log + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append(
        {"operation": "metric_budget_repair", "reason": "companion_ibm_bullets_full_metrics"}
    )
    return new_raw, new_parsed


THEME_REPAIR_RECEIPT_FILENAME = "ibm_narrative_theme_repair_receipt.json"
THEME_REPAIR_REGEN_RAW_FILENAME = "ibm_narrative_theme_repair_regen_raw.txt"
_THEME_BUDGET_MAX_FAMILIES = 4


def _theme_repair_regen_max_tokens(attempt1_raw: str) -> int:
    """Size the regen output cap from attempt 1's observed response length plus margin.

    Live fail (postRungs_20260610_2246): attempt 1 itself stopped at the 1200-token lane cap
    (provider_response.json: stop_reason=max_tokens, output_tokens=1200) and the kept compact
    parse-retry doc (~4.5KB ≈ ~1,130 tokens) left <6% headroom. The rung's regen reused the
    same 1200 cap and truncated again → unterminated JSON → parse_failed. chars/4 token
    estimate × 1.5 margin, floored at the lane default.
    """
    estimated_tokens = (len(attempt1_raw) // 4) + 1
    return max(NARRATIVE_MAX_OUTPUT_TOKENS, (estimated_tokens * 3) // 2)


def _run_ibm_narrative_deterministic_ledger_chain(
    parsed: dict[str, Any],
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Same deterministic chain the lane applies to attempt 1: normalize → remap → decompose → bind."""
    from apps_rg.runtime.sections.ibm_canonical_hydration import (
        bind_missing_ibm_narrative_theme_citations,
        decompose_ibm_narrative_claim_ledger_by_clause,
    )

    out = normalize_parsed_output(parsed, runtime_payload)
    if out is None:
        return None
    remap_ibm_narrative_claim_ledger_to_fact_pool(out, runtime_payload)
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    decompose_ibm_narrative_claim_ledger_by_clause(
        out,
        narrative_sentence=str(out.get("narrative_sentence") or ""),
        allowed_fact_ids=allowed,
    )
    bind_missing_ibm_narrative_theme_citations(out, allowed_fact_ids=allowed)
    return out


def apply_ibm_narrative_theme_overpack_repair(
    *,
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    runtime_generation_status: str,
) -> tuple[str, dict[str, Any] | None, bool]:
    """Theme-overpack rung: ONE bounded same-authority regen before final X2/X3.

    Structural flap (live fail postW4fix_20260610_2200): the clause decomposer splits on
    ', establishing' (maxsplit=1 → max 2 ledger rows) and clause-decomposition allows max 2
    bul_ibm_* roots per row → ledger union ≤ 4 roots. A narrative tripping 5 theme triggers
    can NEVER pass both x2_ibm_narrative_claim_theme_coverage and
    x2_ibm_narrative_claim_ledger_clause_decomposition. This rung mirrors the headline
    content-signal idiom (apply_headline_content_signal_repair, PR #284): fire iff REAL_LLM
    and the theme math is unsatisfiable with the current post-chain ledger; accept fail-closed
    only when the regen parses AND expresses ≤ 4 themes AND the full deterministic ledger
    chain yields theme-coverage and clause-decomposition both passing; else keep attempt 1
    (X2 fails exactly as today). Gates themselves are untouched.
    """
    if not isinstance(parsed, dict) or runtime_generation_status != "REAL_LLM":
        return raw_output, parsed, False
    from apps_rg.runtime.validators.ibm_narrative_x2 import (
        _ledger_fact_ids,
        check_ibm_narrative_claim_ledger_clause_decomposition,
        ibm_narrative_material_fact_ids_for_sentence,
    )
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        proof_source_from_metadata,
    )

    try:
        proof_source = proof_source_from_metadata(runtime_payload.get("proof_pool_metadata"))
    except ValueError:
        # Malformed pool metadata: skip the rung; X2 surfaces the same error downstream.
        return raw_output, parsed, False
    if proof_source in ("srfs", "broad_skills_ledger"):
        # Theme-coverage is pool-membership-only in these modes — no structural overpack math.
        return raw_output, parsed, False
    narrative_pre = str(parsed.get("narrative_sentence") or "").strip()
    if not narrative_pre:
        return raw_output, parsed, False
    themes_pre = ibm_narrative_material_fact_ids_for_sentence(narrative_pre)
    ledger_rows_pre = [r for r in (parsed.get("claim_ledger") or []) if isinstance(r, dict)]
    cited_pre = {s for s in _ledger_fact_ids(ledger_rows_pre) if s.startswith("bul_ibm_")}
    missing_pre = sorted(themes_pre - cited_pre)
    overpacked = len(themes_pre) > _THEME_BUDGET_MAX_FAMILIES
    if not overpacked and not missing_pre:
        return raw_output, parsed, False

    from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, load_ledger, record_repair
    from apps_rg.runtime.sections.ibm_narrative_repair_policy import (
        THEME_REPAIR_MAX_ATTEMPTS,
        theme_repair_enabled,
        theme_repair_env_state,
    )

    ledger_doc = load_ledger(artifact_dir) or {}
    budget_consumed = any(
        r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        for r in (ledger_doc.get("repairs") or [])
    )
    receipt: dict[str, Any] = {
        "section_id": "ibm_narrative",
        "run_id": str(runtime_payload.get("run_id") or ""),
        "gate_id": "x2_ibm_narrative_claim_theme_coverage",
        "fired": False,
        "trigger": {
            "themes_detected_pre": sorted(themes_pre),
            "count_pre": len(themes_pre),
            "missing_in_ledger_union_pre": missing_pre,
            "narrative_pre": narrative_pre,
        },
        "accepted": False,
        "themes_post": sorted(themes_pre),
        "rejected_reason": None,
        "bounded": {"max_attempts": THEME_REPAIR_MAX_ATTEMPTS, "attempts_used": 0},
        "kill_switch": theme_repair_env_state(),
        "regen_max_tokens": None,
        "regen_raw_response_ref": None,
        "regen_parse_error": None,
    }
    accepted = False
    if not theme_repair_enabled():
        receipt["rejected_reason"] = "kill_switch_off"
    elif budget_consumed:
        receipt["rejected_reason"] = "regen_budget_consumed"
    else:
        receipt["fired"] = True
        receipt["bounded"]["attempts_used"] = 1
        theme_ids = ", ".join(sorted(themes_pre))
        repair_messages = [
            *messages,
            {"role": "assistant", "content": raw_output},
            {
                "role": "user",
                "content": (
                    "THEME_BUDGET_REVISION (x2_ibm_narrative_claim_theme_coverage): your "
                    f"narrative_sentence materially expresses {len(themes_pre)} theme families "
                    f"[{theme_ids}]; the deterministic ledger math (', establishing' split = max 2 "
                    "claim_ledger rows, max 2 bul_ibm_* roots per row) cannot cover more than 4 themes "
                    f"total and 2 per clause (currently uncovered: [{', '.join(missing_pre)}]). "
                    "Rewrite narrative_sentence expressing AT MOST 4 theme families — at most 2 per "
                    "clause — preserving the clause structure ', establishing'. Keep every other "
                    "constraint (exactly one sentence, IBM anchor once, no metric replay, no em dash, "
                    "no candidate name, claim_ledger rows with at most 2 bul_ibm_* roots each from "
                    "ALLOWED_SOURCE_FACT_IDS). Return one NEW compact JSON object only. "
                    "Keys: narrative_sentence (one sentence), selected_fact_plan, claim_ledger, "
                    "jd_alignment, gap_notes, change_log, self_check."
                ),
            },
        ]
        regen_max_tokens = _theme_repair_regen_max_tokens(raw_output)
        receipt["regen_max_tokens"] = regen_max_tokens
        repair_payload = {
            **provider_payload,
            "messages": repair_messages,
            "max_tokens": regen_max_tokens,
        }
        result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
        regen_raw = str(result.raw_model_output or "")
        (artifact_dir / THEME_REPAIR_REGEN_RAW_FILENAME).write_text(
            regen_raw, encoding="utf-8"
        )
        receipt["regen_raw_response_ref"] = THEME_REPAIR_REGEN_RAW_FILENAME
        if result.runtime_generation_status != "REAL_LLM":
            receipt["rejected_reason"] = "provider_not_real"
        else:
            new_raw = regen_raw
            new_parsed, _err = parse_model_json(new_raw)
            if new_parsed is None:
                receipt["rejected_reason"] = "parse_failed"
                receipt["regen_parse_error"] = _err
            else:
                new_parsed = _run_ibm_narrative_deterministic_ledger_chain(
                    new_parsed, runtime_payload
                )
                if new_parsed is None:
                    receipt["rejected_reason"] = "parse_failed"
                    receipt["regen_parse_error"] = (
                        "deterministic ledger chain returned None (normalize_parsed_output)"
                    )
                else:
                    narrative_post = str(new_parsed.get("narrative_sentence") or "").strip()
                    themes_post = ibm_narrative_material_fact_ids_for_sentence(narrative_post)
                    rows_post = [
                        r for r in (new_parsed.get("claim_ledger") or []) if isinstance(r, dict)
                    ]
                    cited_post = {
                        s for s in _ledger_fact_ids(rows_post) if s.startswith("bul_ibm_")
                    }
                    clause_ok, _detail = check_ibm_narrative_claim_ledger_clause_decomposition(
                        narrative_post, rows_post
                    )
                    receipt["themes_post"] = sorted(themes_post)
                    if not narrative_post:
                        receipt["rejected_reason"] = "empty_narrative"
                    elif len(themes_post) > _THEME_BUDGET_MAX_FAMILIES:
                        receipt["rejected_reason"] = "themes_still_overpacked"
                    elif themes_post - cited_post:
                        receipt["rejected_reason"] = "theme_coverage_unsatisfied"
                    elif not clause_ok:
                        receipt["rejected_reason"] = "clause_decomposition_failed"
                    else:
                        prior_log = (
                            list(parsed.get("change_log") or [])
                            if isinstance(parsed.get("change_log"), list)
                            else []
                        )
                        new_parsed["change_log"] = prior_log + list(
                            new_parsed.get("change_log") or []
                        )
                        new_parsed["change_log"].append(
                            {
                                "operation": "ibm_narrative_theme_overpack_repair",
                                "reason": "x2_ibm_narrative_claim_theme_coverage:overpack",
                            }
                        )
                        record_repair(
                            artifact_dir,
                            kind=KIND_REGEN_LLM,
                            operation="ibm_narrative_theme_overpack_repair",
                            reason="x2_ibm_narrative_claim_theme_coverage:overpack",
                            replaced_l2=True,
                        )
                        raw_output, parsed, accepted = new_raw, new_parsed, True
                        receipt["accepted"] = True
    write_json(artifact_dir / THEME_REPAIR_RECEIPT_FILENAME, receipt)
    return raw_output, parsed, accepted


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    narrative = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services, establishing reliability and governance discipline for governed analytics delivery."
    )
    allowed_sorted = list(runtime_payload.get("allowed_fact_ids") or [])
    bases = [str(x) for x in allowed_sorted if str(x).strip()][:6]
    if len(bases) >= 3:
        ledger = [
            {
                "claim_text": (
                    "At IBM, led enterprise-scale modernization across cloud and analytics programs "
                    "for regulated financial services"
                ),
                "source_fact_ids": bases[:2],
            },
            {"claim_text": "establishing lineage and observability foundations", "source_fact_ids": [bases[2]]},
            {
                "claim_text": "hyperscaler partnership discipline for platform modernization and ecosystem execution",
                "source_fact_ids": bases[3:5] if len(bases) > 3 else [bases[-1]],
            },
        ]
    else:
        ledger = [
            {
                "claim_text": (
                    "At IBM, led enterprise-scale modernization across cloud and analytics programs "
                    "for regulated financial services"
                ),
                "source_fact_ids": ["bul_ibm_001", "bul_ibm_002"],
            },
            {
                "claim_text": "establishing lineage and observability foundations",
                "source_fact_ids": ["bul_ibm_004"],
            },
            {
                "claim_text": "hyperscaler partnership discipline for platform modernization and ecosystem execution",
                "source_fact_ids": ["bul_ibm_005"],
            },
        ]
    return {
        "narrative_sentence": narrative,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": ledger,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "deterministic_fixture"}],
        "self_check": {"one_sentence": True, "third_person": True},
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
        pass_reason="REAL_LLM output passed all deterministic ibm_narrative gates.",
        artifact_dir=artifact_dir,
    )


def write_x2_gate_outputs(
    path: Path,
    gates: list[dict[str, Any]],
    *,
    section_id: str | None = "ibm_narrative",
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


"""Compat lazy re-export — canonical: apps_rg.runtime.sections.ibm_narrative_lane_execution."""

_LANE_EXEC_EXPORTS = frozenset({"run_ibm_narrative_execution", "run_ibm_narrative_lane_execution"})


def __getattr__(name: str) -> Any:
    if name in _LANE_EXEC_EXPORTS:
        from apps_rg.runtime.sections import ibm_narrative_lane_execution as _lane

        return getattr(_lane, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | _LANE_EXEC_EXPORTS)


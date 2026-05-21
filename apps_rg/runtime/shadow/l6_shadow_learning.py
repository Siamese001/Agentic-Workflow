"""L6 shadow learning record — observation only after X3 (future-run recommendations).

Emitted to ``l6_shadow_learning.json`` in the lane artifact dir. Read-only with respect to
production artifacts: no mutations to x3_disposition, claim ledger, X2, parsed output, or exit code.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import (
    repo_rel,
    summarize_x1d,
    summarize_x2,
    summarize_x3,
)

L6_LEARNING_KIND = "l6_shadow_learning"
L6_LEARNING_VERSION = "1"


def _load_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def _ref(repo_root: Path, artifact_dir: Path, name: str) -> str | None:
    p = artifact_dir / name
    if not p.is_file():
        return None
    return repo_rel(repo_root, p)


def build_l6_shadow_learning_record(
    *,
    artifact_dir: Path,
    repo_root: Path,
    section_id: str,
    lane_key: str,
) -> dict[str, Any]:
    """Build inert L6 shadow learning JSON from completed-run artifacts (post X3).

    Does not write any files. If upstream refs are missing, returns a blocked/inert record.
    """
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()

    x3_path = ad / "x3_disposition.json"
    x3_raw = _load_json(x3_path)
    if not isinstance(x3_raw, dict) or not x3_raw.get("x3_code"):
        missing: list[str] = []
        if not x3_path.is_file():
            missing.append("x3_disposition.json")
        return {
            "artifact_kind": L6_LEARNING_KIND,
            "l6_learning_version": L6_LEARNING_VERSION,
            "section_id": section_id,
            "lane_key": lane_key,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_boundary_observed": False,
            "shadow_status": "inert_blocked_missing_upstream",
            "missing_upstream_refs": missing or ["x3_disposition.json unreadable or empty"],
            "input_refs": {},
            "consumed_x3_code": None,
            "consumed_x2_blocking_failures": [],
            "claim_text_gap_observed": False,
            "support_gap_observed": False,
            "judge_gap_observed": False,
            "consumed_proof_eligible_snapshot": None,
            "consumed_judge_proof_eligible_snapshot": None,
            "recommendation_records": [],
            "current_run_mutation_assertion": False,
            "current_run_rescue_assertion": False,
            "durable_write_assertion": False,
            "notes": "L6 shadow learning blocked: X3 or upstream refs unavailable. Inert only.",
        }

    x2_raw = _load_json(ad / "x2_gate_outputs.json")
    x1_raw = _load_json(ad / "x1d_llm_judge_outputs.json")
    parsed_raw = _load_json(ad / "parsed_output.json")
    cov_raw = _load_json(ad / "text_claim_coverage.json")
    canon_raw = _load_json(ad / "canonical_claim_ledger_v2.json")
    usage_ledger_raw = _load_json(ad / "section_input_usage_ledger.json")

    x2 = x2_raw if isinstance(x2_raw, dict) else {}
    x1 = x1_raw if isinstance(x1_raw, dict) else {}
    x2_sum = summarize_x2(x2)
    x1_sum = summarize_x1d(x1)
    x3_sum = summarize_x3(x3_raw)

    failed_ids = list(x2_sum.get("failed_gate_ids") or [])

    parse_status = ""
    if isinstance(parsed_raw, dict):
        parse_status = str(parsed_raw.get("parse_status") or "")

    claim_text_gap = (
        "x2_claim_ledger_claim_text_non_empty" in failed_ids
        or parse_status not in ("", "OK")
    )

    support_gap = False
    if isinstance(cov_raw, dict) and cov_raw.get("overall_pass") is False:
        support_gap = True
    for gid in (
        "x2_unify_narrative_source_supported",
        "x2_unify_narrative_unify_only_fact_scope",
        "x2_unify_narrative_targeting_inputs_used_but_not_proof",
        "x2_no_bullet_label_repetition",
        "x2_no_companion_ngram_copy",
        "x2_unify_narrative_word_budget",
        "x2_section_claims_supported_by_base_resume",
        "x2_jd_used_as_required_targeting_input",
        "x2_briefing_used_as_required_context_input",
        "x2_title_company_used_as_required_positioning_input",
        "x2_no_non_evidence_inputs_as_claim_evidence",
        "x2_no_non_evidence_inputs_in_source_fact_ids",
        "x2_selected_fact_ids_only",
        "x2_input_usage_accounting_consistent",
        "x2_section_input_usage_ledger_present",
    ):
        if gid in failed_ids:
            support_gap = True
            break

    authority_usage_risk = False
    if isinstance(usage_ledger_raw, dict):
        eb = usage_ledger_raw.get("evidence_boundary") or {}
        if isinstance(eb, dict):
            if eb.get("non_evidence_inputs_used_as_claim_evidence") is True:
                authority_usage_risk = True
            if eb.get("non_evidence_inputs_in_source_fact_ids") is True:
                authority_usage_risk = True
        css = usage_ledger_raw.get("claim_support_summary") or {}
        if int(css.get("unsupported_claim_count") or 0) > 0:
            authority_usage_risk = True

    judge_gap = bool(
        x1_sum.get("mocked_judges")
        or x1_sum.get("blocked_judges")
        or x1_sum.get("soft_failed_judges")
        or x1_sum.get("decisive_failures")
    )

    recs: list[dict[str, Any]] = []
    if claim_text_gap:
        recs.append(
            {
                "applies_to": "future_run_only",
                "recommendation": (
                    "Strengthen model output so claim_ledger rows include non-empty claim_text "
                    "and source_fact_ids drawn exactly from ALLOWED_SOURCE_FACT_IDS."
                ),
            }
        )
    if support_gap:
        recs.append(
            {
                "applies_to": "future_run_only",
                "recommendation": (
                    "Review Unify fact scope and sentence–claim coverage so narrative evidence "
                    "maps to allowed bul_unify_* sources."
                ),
            }
        )
    if judge_gap:
        recs.append(
            {
                "applies_to": "future_run_only",
                "recommendation": (
                    "Replace blocked/mocked judges with approved model-backed evaluators when "
                    "production proof is required; no judge mutation on this run."
                ),
            }
        )
    if authority_usage_risk:
        recs.append(
            {
                "applies_to": "future_run_only",
                "recommendation": (
                    "Review section_input_usage_ledger.json: JD/briefing/title/company are mandatory non-evidence "
                    "inputs; keep claim evidence on selected base-resume facts only; trim any non-evidence "
                    "wording presented as factual resume claims."
                ),
            }
        )
    if failed_ids:
        recs.append(
            {
                "applies_to": "future_run_only",
                "recommendation": (
                    f"Address failed deterministic gates for a future run: {', '.join(failed_ids)}. "
                    "No automatic X3 rescue or ledger repair on this run."
                ),
            }
        )

    proof_elig = x3_raw.get("proof_eligible")
    judge_proof_elig = x3_raw.get("judge_proof_eligible")

    return {
        "artifact_kind": L6_LEARNING_KIND,
        "l6_learning_version": L6_LEARNING_VERSION,
        "section_id": section_id,
        "lane_key": lane_key,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_boundary_observed": True,
        "shadow_status": "observed_post_x3",
        "input_refs": {
            "runtime_proof_run_dir_repo_relative": repo_rel(rr, ad),
            "compiled_prompt_artifact_ref": _ref(rr, ad, "compiled_prompt_artifact.json"),
            "compiled_prompt_txt_ref": _ref(rr, ad, "compiled_prompt.txt"),
            "provider_request_ref": _ref(rr, ad, "provider_request.json"),
            "provider_response_ref": _ref(rr, ad, "provider_response.json"),
            "parsed_output_ref": _ref(rr, ad, "parsed_output.json"),
            "canonical_claim_ledger_v2_ref": _ref(rr, ad, "canonical_claim_ledger_v2.json"),
            "text_claim_coverage_ref": _ref(rr, ad, "text_claim_coverage.json"),
            "section_input_usage_ledger_ref": _ref(rr, ad, "section_input_usage_ledger.json"),
            "x2_gate_outputs_ref": _ref(rr, ad, "x2_gate_outputs.json"),
            "x3_disposition_ref": _ref(rr, ad, "x3_disposition.json"),
            "x1d_llm_judge_outputs_ref": _ref(rr, ad, "x1d_llm_judge_outputs.json"),
            "l2_output_ref": _ref(rr, ad, "l2_output.json"),
            "l6_shadow_eval_package_ref": _ref(rr, ad, "l6_shadow_eval_package.json"),
        },
        "consumed_x3_code": x3_sum.get("x3_code"),
        "consumed_x2_blocking_failures": failed_ids,
        "claim_text_gap_observed": claim_text_gap,
        "support_gap_observed": support_gap,
        "judge_gap_observed": judge_gap,
        "consumed_proof_eligible_snapshot": proof_elig,
        "consumed_judge_proof_eligible_snapshot": judge_proof_elig,
        "x2_summary_snapshot": x2_sum,
        "x1d_summary_snapshot": {k: v for k, v in x1_sum.items() if k != "judge_scores"},
        "x3_summary_snapshot": x3_sum,
        "canonical_claim_ledger_parse_ok": isinstance(canon_raw, dict)
        and str(canon_raw.get("parse_status") or "") == "OK",
        "recommendation_records": recs,
        "current_run_mutation_assertion": False,
        "current_run_rescue_assertion": False,
        "durable_write_assertion": False,
        "notes": (
            "L6 shadow learning: future-run recommendations only. "
            "No mutation, rescue, promotion, L4/memory/policy writes, or exit semantics changes on this run."
        ),
    }


__all__ = [
    "L6_LEARNING_KIND",
    "L6_LEARNING_VERSION",
    "build_l6_shadow_learning_record",
]

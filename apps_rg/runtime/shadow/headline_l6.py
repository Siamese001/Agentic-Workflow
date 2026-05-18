"""L6 shadow handoff for headline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict, repo_rel

SECTION_ID = "headline"


def build_l6_shadow_package(
    *,
    artifact_dir: Path,
    repo_root: Path,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
) -> dict[str, Any]:
    return build_l6_shadow_handoff_dict(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=SECTION_ID,
        prompt_id=prompt_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def emit_headline_l6_shadow_learning_outputs(
    *,
    repo_root: Path,
    artifact_dir: Path,
    handoff_pkt: dict[str, Any],
    prompt_hash: str,
    final_headline_line: str,
    x2_passed: bool,
    x3_record: dict[str, Any],
    observed_failures: list[str],
    support_coverage_findings: list[str],
    proof_misuse_findings: list[str],
    banned_content_findings: list[str],
    phrasing_quality_findings: list[str],
    future_run_recommendations: list[str],
    prompt_control_receipt_findings: list[str] | None = None,
    raw_schema_findings: list[str] | None = None,
    self_check_findings: list[str] | None = None,
    l2_output_ref: str | None = None,
    reasoning_execution_receipt_summary: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    """Offline-only L6 headline artifacts under artifacts/apps_rg/l6/headline/<run_id>/."""
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()
    run_id = str(handoff_pkt.get("run_id") or ad.name)
    out_root = rr / "artifacts" / "apps_rg" / "l6" / "headline" / run_id
    out_root.mkdir(parents=True, exist_ok=True)
    json_path = out_root / "headline_l6_shadow_eval.json"
    md_path = out_root / "headline_l6_shadow_summary.md"

    x3_code = str(x3_record.get("x3_code") or "")
    sealed_ref = repo_rel(rr, ad / "headline_output.txt")
    model_ref = repo_rel(rr, ad / "provider_response.json")
    l2_ref = l2_output_ref or repo_rel(rr, ad / "l2_output.json")
    pr_findings = list(prompt_control_receipt_findings or [])
    raw_findings = list(raw_schema_findings or [])
    sc_findings = list(self_check_findings or [])
    rsum = reasoning_execution_receipt_summary or {}

    eval_payload: dict[str, Any] = {
        "section_id": SECTION_ID,
        "run_id": run_id,
        "prompt_hash": prompt_hash,
        "compiled_prompt_ref": repo_rel(rr, ad / "compiled_prompt.txt"),
        "compiled_prompt_artifact_ref": repo_rel(rr, ad / "compiled_prompt_artifact.json"),
        "sealed_artifact_ref": sealed_ref,
        "x1_refs": repo_rel(rr, ad / "x1d_llm_judge_outputs.json"),
        "x2_refs": repo_rel(rr, ad / "x2_gate_outputs.json"),
        "x3_ref": repo_rel(rr, ad / "x3_disposition.json"),
        "claim_ledger_ref": repo_rel(rr, ad / "claim_ledger.json"),
        "selected_fact_plan_ref": repo_rel(rr, ad / "selected_fact_plan.json"),
        "evidence_refs": [
            repo_rel(rr, ad / "runtime_payload.json"),
            repo_rel(rr, ad / "prompt_selection_trace.json"),
            repo_rel(rr, ad / "fact_check_result.json"),
        ],
        "model_output_ref": model_ref,
        "final_headline_line": final_headline_line,
        "offline_only": True,
        "current_run_effect": False,
        "runtime_disposition_unchanged": True,
        "observed_failures": observed_failures,
        "support_coverage_findings": support_coverage_findings,
        "proof_misuse_findings": proof_misuse_findings,
        "banned_content_findings": banned_content_findings,
        "phrasing_quality_findings": phrasing_quality_findings,
        "future_run_recommendations": future_run_recommendations,
        "promotion_candidate": False,
        "handoff_packet_repo_relative": handoff_pkt.get("l6_shadow_eval_package_repo_relative"),
        "l2_output_ref": l2_ref,
        "prompt_control_receipt_findings": pr_findings,
        "raw_schema_findings": raw_findings,
        "self_check_findings": sc_findings,
        "reasoning_execution_receipt_summary": rsum,
    }
    json_path.write_text(json.dumps(eval_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md_lines = [
        "# Headline L6 shadow summary",
        "",
        f"- Runtime disposition (X3): `{x3_code}`",
        f"- Headline passed X2: `{x2_passed}`",
        "- Evidence coverage (shadow scan): see `support_coverage_findings` in JSON.",
        f"- Proof misuse findings: {proof_misuse_findings or 'none'}",
        f"- Prompt-control / reasoning receipt findings: {pr_findings or 'none'}",
        f"- Raw claim_ledger schema findings: {raw_findings or 'none'}",
        f"- Self-check vs runtime findings: {sc_findings or 'none'}",
        f"- L2 output ref: `{l2_ref}`",
        f"- Reasoning receipt summary (bundle): `{json.dumps(rsum, sort_keys=True)}`",
        "- Prompt/rubric drift (shadow): see `phrasing_quality_findings` / `future_run_recommendations` in JSON.",
        f"- Recommended future-run tuning: {future_run_recommendations or 'none'}",
        "",
        "**L6 shadow output did not affect this run.**",
        "",
    ]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return json_path, md_path


__all__ = ["build_l6_shadow_package", "emit_headline_l6_shadow_learning_outputs", "SECTION_ID"]

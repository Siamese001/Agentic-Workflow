"""Dimension → upstream Qwen/L2 debug triangulation (no extra judge spend)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    EXEC_SUMMARY_RUBRIC_DIMENSION_IDS,
    build_x1d_dimension_matrix,
    collect_dimension_remediation_lines,
)
from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    dimension_gate_map,
)

TRIANGULATION_SCHEMA = "executive_summary_dimension_upstream_triangulation_v1"

# Rubric dimensions that are primarily fixed by L2/Qwen + composition (not a full re-panel).
L2_UPSTREAM_DIMENSIONS: frozenset[str] = frozenset(
    {
        "executive_signal",
        "resume_voice",
        "ats_alignment_without_keyword_stuffing",
        "synthesis_quality",
        "evidence_utilization",
        "anti_overfit",
    }
)

DIMENSION_QWEN_SURFACES: dict[str, tuple[str, ...]] = {
    "factual_support": (
        "claim_ledger.json",
        "canonical_claim_ledger_v2.json",
        "allowed_fact_packet in compiled_prompt.txt",
    ),
    "executive_signal": (
        "compiled_prompt.txt (I0 opener + E0 examples order)",
        "executive_summary_composition_plan.json (sentence_arc)",
        "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml",
    ),
    "resume_voice": (
        "compiled_prompt.txt (Y0 / voice guards)",
        "executive_summary_finalize_coherence.json",
    ),
    "ats_alignment_without_keyword_stuffing": (
        "compiled_prompt.txt (JD_TEXT + BRIEFING blocks)",
        "targeting_context_parity_receipt.json",
        "GRAPH_TARGETING_CAPSULE in executive_summary_pa.py",
    ),
    "anti_overfit": (
        "compiled_prompt.txt (proof law / jd_used_as_proof=false)",
        "claim_ledger source_fact_ids",
    ),
    "synthesis_quality": (
        "compiled_prompt.txt (six-sentence arc + synthesis guards)",
        "executive_summary_composition_plan.json",
        "synthesis_regen_receipt.json",
        "provider_response.json (L2 raw)",
    ),
    "evidence_utilization": (
        "selected_fact_plan.json",
        "compiled_prompt.txt (ALLOWED_SOURCE_FACT_IDS)",
        "text_claim_coverage.json",
    ),
    "deterministic_alignment": (
        "x2_gate_outputs.json",
        "executive_summary_judge_packet_post_x2.json (deterministic_gate_summary)",
    ),
}

DIMENSION_UPSTREAM_ACTIONS: dict[str, tuple[str, ...]] = {
    "executive_signal": (
        "Lead with SVP strategy thesis in S1; avoid achievement-inventory S2–S5 stack.",
        "Use active voice; connect platform + governance + commercial arcs.",
    ),
    "synthesis_quality": (
        "Enforce connective tissue S3–S6 per composition_plan sentence_arc.",
        "Avoid comma-chain mechanism dumps; one integrated paragraph.",
    ),
    "ats_alignment_without_keyword_stuffing": (
        "Weave EA/interoperability/innovation themes from briefing via allowed facts only.",
        "Never name TARGET_COMPANY; no JD-as-proof in claim_ledger.",
    ),
    "resume_voice": (
        "Remove recruiter filler and passive stacks; third person only.",
    ),
    "evidence_utilization": (
        "Weave unused allowed_fact_ids from selected_fact_plan into claim_ledger rows.",
    ),
    "factual_support": (
        "Every sentence must cite allowed source_fact_ids; no orphan claims.",
    ),
    "anti_overfit": (
        "Do not treat JD/briefing text as experience proof.",
    ),
    "deterministic_alignment": (
        "Fix X2 failures before re-spending on judges; judges mirror gate snapshot.",
    ),
}


def consensus_failed_dimensions(
    x1d_judges: list[dict[str, Any]],
    *,
    min_fail_count: int = 2,
) -> list[str]:
    """Dimensions with >= min_fail_count judge fails or matrix consensus_fail."""
    matrix = build_x1d_dimension_matrix(x1d_judges)
    failed: list[str] = []
    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        agg = matrix.get("by_dimension", {}).get(dim) or {}
        fc = int(agg.get("fail_count") or 0)
        if fc >= min_fail_count or agg.get("consensus_fail") is True:
            failed.append(dim)
    return failed


def dimension_major_fail_on_judge(judge: dict[str, Any], dimension_id: str) -> bool:
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        dimension_major_fail_on_judge as _dim_major_fail,
    )

    return _dim_major_fail(judge, dimension_id)


def solitary_dimension_severe_soft_fail(soft_judge: dict[str, Any]) -> tuple[bool, list[str]]:
    """True when one soft-failed judge has major fail on an L2-upstream dimension."""
    dims: list[str] = []
    for dim in L2_UPSTREAM_DIMENSIONS:
        if dimension_major_fail_on_judge(soft_judge, dim):
            dims.append(dim)
    return bool(dims), dims


def build_dimension_upstream_triangulation(
    *,
    x1d_judges: list[dict[str, Any]],
    x2_failed_gate_ids: list[str] | None = None,
    generation_manifest: dict[str, Any] | None = None,
    judge_regen_cycles: dict[str, Any] | None = None,
    post_regen_judge_mode: str = "soft_failed_only",
) -> dict[str, Any]:
    """Operator/debug artifact: map dimension failures → Qwen files and actions."""
    matrix = build_x1d_dimension_matrix(x1d_judges)
    dim_lines = collect_dimension_remediation_lines(x1d_judges, min_fail_count=1)
    gate_map = dimension_gate_map()
    x2_failed = list(x2_failed_gate_ids or [])
    consensus = consensus_failed_dimensions(x1d_judges, min_fail_count=2)
    l2_upstream = [d for d in consensus if d in L2_UPSTREAM_DIMENSIONS]

    per_dimension: list[dict[str, Any]] = []
    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        agg = matrix.get("by_dimension", {}).get(dim) or {}
        fc = int(agg.get("fail_count") or 0)
        if fc < 1 and not agg.get("consensus_fail"):
            continue
        related_x2 = gate_map.get(dim, "")
        per_dimension.append(
            {
                "dimension_id": dim,
                "fail_count": fc,
                "consensus_fail": bool(agg.get("consensus_fail")),
                "primary_surface": "l2_qwen" if dim in L2_UPSTREAM_DIMENSIONS else "x2_or_judge_packet",
                "related_x2_gate": related_x2,
                "x2_gate_failed_in_run": related_x2 in x2_failed if related_x2 else False,
                "qwen_prompt_surfaces": list(DIMENSION_QWEN_SURFACES.get(dim, ())),
                "upstream_actions": list(DIMENSION_UPSTREAM_ACTIONS.get(dim, ())),
            }
        )

    regen_cycles = int((judge_regen_cycles or {}).get("max_cycles") or 0)
    cycles_run = len((judge_regen_cycles or {}).get("cycles") or [])

    if x2_failed and not x1d_judges:
        recommended = (
            "X2 blocked judges — fix deterministic gates first (see x2_gate_outputs.json); "
            "review compiled_prompt.txt + composition_plan before any judge spend."
        )
    elif l2_upstream:
        recommended = (
            f"L2/Qwen upstream fix recommended for: {', '.join(l2_upstream)}. "
            "Review qwen_prompt_surfaces; use DIMENSION_VERDICTS in judge_remediation_cycles "
            f"before paying for more judge panels (post_regen mode={post_regen_judge_mode})."
        )
    elif consensus:
        recommended = "Address consensus_failed_dimensions before additional judge cycles."
    else:
        recommended = "No dimension consensus failure; holistic scores may still be below threshold."

    return {
        "schema": TRIANGULATION_SCHEMA,
        "consensus_failed_dimensions": consensus,
        "l2_upstream_failed_dimensions": l2_upstream,
        "dimension_remediation_lines": dim_lines,
        "per_dimension": per_dimension,
        "qwen_prompt_refs": {
            "compiled_prompt": "compiled_prompt.txt",
            "compiled_prompt_artifact": "compiled_prompt_artifact.json",
            "provider_request": "provider_request.json",
            "provider_response": "provider_response.json",
            "raw_model_output": "raw_model_output.txt",
            "composition_plan": "executive_summary_composition_plan.json",
            "generation_grade_contract_manifest": "generation_grade_contract_manifest.json",
        },
        "judge_cost_controls": {
            "post_regen_judge_rescore_mode": post_regen_judge_mode,
            "judge_regen_max_cycles_configured": regen_cycles,
            "judge_regen_cycles_consumed": cycles_run,
            "note": "Post-regen should rescore soft-failed judges only unless APPS_RG_EXEC_SUMMARY_POST_REGEN_JUDGE_MODE=full_panel.",
        },
        "generation_manifest_digest": (generation_manifest or {}).get("instructional_digests"),
        "recommended_next_step": recommended,
    }


def write_dimension_upstream_triangulation(
    path: Path,
    body: dict[str, Any],
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


__all__ = [
    "DIMENSION_QWEN_SURFACES",
    "L2_UPSTREAM_DIMENSIONS",
    "TRIANGULATION_SCHEMA",
    "build_dimension_upstream_triangulation",
    "consensus_failed_dimensions",
    "dimension_major_fail_on_judge",
    "solitary_dimension_severe_soft_fail",
    "write_dimension_upstream_triangulation",
]

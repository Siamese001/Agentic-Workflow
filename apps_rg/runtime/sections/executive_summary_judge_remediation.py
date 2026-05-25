"""Post-X1D judge-informed Qwen remediation for executive_summary (apps_rg only)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_repair_policy import (
    judge_regen_legacy_remediation_block_enabled,
    judge_regen_max_attempts,
    judge_regen_prescriptive_delta_enabled,
    judge_regeneration_enabled,
    judge_safe_prefilter_enabled,
    post_regen_judge_rescore_mode,
    post_x2_judge_refresh_enabled,
    POST_REGEN_JUDGE_RESCORE_FULL_PANEL,
    POST_REGEN_JUDGE_RESCORE_SOFT_ONLY,
)
from apps_rg.runtime.sections.executive_summary_upstream_triangulation import (
    consensus_failed_dimensions,
    solitary_dimension_severe_soft_fail,
)
from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

_SYNTHESIS_TAXONOMY = frozenset(
    {
        "synthesis",
        "bullet",
        "stack",
        "staccato",
        "weave",
        "integrated",
        "paragraph",
        "narrative",
    }
)
_EXEC_SIGNAL_TAXONOMY = frozenset(
    {
        "executive_signal",
        "svp",
        "strategic",
        "platform",
        "governance",
        "commercial",
        "innovation",
    }
)
_JD_TAXONOMY = frozenset(
    {
        "jd",
        "briefing",
        "targeting",
        "innovation",
        "enterprise architecture",
        "it strategy",
    }
)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _coerce_judge_dict(judge: Any) -> dict[str, Any]:
    if isinstance(judge, dict):
        return judge
    to_dict = getattr(judge, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    return dict(judge)  # type: ignore[arg-type]


def _normalize_judge_list(judges: list[Any]) -> list[dict[str, Any]]:
    return [_coerce_judge_dict(j) for j in judges]


def _judge_text_blob(judge: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("findings", "fail_reasons", "quality_flags", "remediation_suggestions"):
        val = judge.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif val:
            parts.append(str(val))
    if judge.get("rationale"):
        parts.append(str(judge.get("rationale")))
    return " ".join(parts).lower()


def _taxonomy_tags(blob: str) -> set[str]:
    tags: set[str] = set()
    if any(t in blob for t in _SYNTHESIS_TAXONOMY):
        tags.add("synthesis")
    if any(t in blob for t in _EXEC_SIGNAL_TAXONOMY):
        tags.add("executive_signal")
    if any(t in blob for t in _JD_TAXONOMY):
        tags.add("jd_emphasis")
    return tags


def all_model_backed_judges_pass(x1d_judges: list[Any]) -> bool:
    norm = _normalize_judge_list(x1d_judges)
    model_backed = [j for j in norm if j.get("evaluator_mode") == "MODEL_BACKED"]
    if not model_backed:
        return False
    return all(
        j.get("provider_status") == "MODEL_BACKED_PASS"
        and j.get("pass") is True
        and not j.get("decisive_failure")
        for j in model_backed
    )


def any_model_backed_soft_fail(x1d_judges: list[Any]) -> bool:
    return any(_is_model_backed_soft_fail(j) for j in _normalize_judge_list(x1d_judges))


def _is_model_backed_soft_fail(judge: dict[str, Any]) -> bool:
    if judge.get("evaluator_mode") != "MODEL_BACKED":
        return False
    if judge.get("decisive_failure"):
        return False
    if judge.get("provider_status") == "MODEL_BACKED_FAIL":
        return True
    if judge.get("pass") is False:
        return True
    ns = judge.get("normalized_score")
    nt = judge.get("normalized_threshold")
    if ns is not None and nt is not None:
        return float(ns) < float(nt)
    return False


def _median_normalized_score(judges: list[dict[str, Any]]) -> float | None:
    scores: list[float] = []
    for j in judges:
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        ns = j.get("normalized_score")
        if ns is None:
            continue
        try:
            scores.append(float(ns))
        except (TypeError, ValueError):
            continue
    if not scores:
        return None
    scores.sort()
    mid = len(scores) // 2
    if len(scores) % 2:
        return scores[mid]
    return (scores[mid - 1] + scores[mid]) / 2.0


def evaluate_judge_remediation_trigger(
    x1d_judges: list[Any],
    *,
    runtime_generation_status: str,
    x2_passed: bool,
) -> tuple[bool, dict[str, Any]]:
    """Return whether post-judge Qwen regen should run (X2 must already be green)."""
    x1d_judges = _normalize_judge_list(x1d_judges)
    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_remediation_trigger_v1",
        "triggered": False,
        "runtime_generation_status": runtime_generation_status,
        "x2_passed": x2_passed,
    }
    if runtime_generation_status != "REAL_LLM" or not x2_passed:
        receipt["reason"] = "requires_real_llm_and_x2_pass"
        return False, receipt

    pass_count = sum(
        1
        for j in x1d_judges
        if j.get("evaluator_mode") == "MODEL_BACKED"
        and j.get("provider_status") == "MODEL_BACKED_PASS"
        and j.get("pass") is True
        and not j.get("decisive_failure")
    )
    receipt["model_backed_pass_count"] = pass_count

    soft_fails = [j for j in x1d_judges if _is_model_backed_soft_fail(j)]
    receipt["soft_fail_count"] = len(soft_fails)
    min_fail = _env_int("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MIN_FAIL_COUNT", 2)
    median_threshold = _env_float("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MEDIAN_THRESHOLD", 0.75)

    tag_sets = [_taxonomy_tags(_judge_text_blob(j)) for j in soft_fails]
    shared_tags: set[str] = set()
    if tag_sets:
        shared_tags = set.intersection(*tag_sets) if len(tag_sets) > 1 else tag_sets[0]

    dim_consensus = consensus_failed_dimensions(x1d_judges, min_fail_count=min_fail)
    receipt["dimension_consensus_failed"] = dim_consensus

    quorum = len(soft_fails) >= min_fail and (bool(shared_tags) or bool(dim_consensus))
    solitary_severe = False
    solitary_dim_major: list[str] = []
    if len(soft_fails) == 1:
        solo = soft_fails[0]
        solo_tags = tag_sets[0] if tag_sets else set()
        dim_severe, solitary_dim_major = solitary_dimension_severe_soft_fail(solo)
        try:
            solo_ns = float(solo.get("normalized_score"))
            solo_nt = float(solo.get("normalized_threshold", 0.8))
            solitary_severe = solo_ns < solo_nt and (
                dim_severe or bool(solo_tags & {"synthesis", "executive_signal", "jd_emphasis"})
            )
        except (TypeError, ValueError):
            solitary_severe = dim_severe
    receipt["solitary_severe_soft_fail"] = solitary_severe
    receipt["solitary_dimension_major_failed"] = solitary_dim_major

    if pass_count >= 2 and not solitary_severe:
        receipt["reason"] = "two_or_more_judges_already_pass_skip_regen"
        return False, receipt

    median = _median_normalized_score(x1d_judges)
    receipt["median_normalized_score"] = median
    median_fail = median is not None and median < median_threshold

    decisive_dims = []
    for j in x1d_judges:
        if not j.get("decisive_failure"):
            continue
        blob = _judge_text_blob(j)
        if "synthesis" in blob or "executive_signal" in blob or "executive signal" in blob:
            decisive_dims.append(j.get("provider_key") or "unknown")
    decisive_trigger = bool(decisive_dims)
    receipt["decisive_synthesis_providers"] = decisive_dims
    receipt["quorum_shared_tags"] = sorted(shared_tags)
    receipt["quorum_soft_fail"] = quorum
    receipt["median_fail"] = median_fail

    triggered = quorum or median_fail or decisive_trigger or solitary_severe
    receipt["triggered"] = triggered
    if triggered:
        if dim_consensus and quorum:
            receipt["trigger_mode"] = "dimension_consensus_soft_fail"
        elif quorum:
            receipt["trigger_mode"] = "quorum_soft_fail"
        elif solitary_severe and solitary_dim_major:
            receipt["trigger_mode"] = "solitary_dimension_major_soft_fail"
        elif solitary_severe:
            receipt["trigger_mode"] = "solitary_severe_soft_fail"
        elif median_fail:
            receipt["trigger_mode"] = "median_normalized_below_threshold"
        else:
            receipt["trigger_mode"] = "decisive_synthesis_or_executive_signal"
    else:
        receipt["reason"] = "no_quorum_median_or_decisive_trigger"
    return triggered, receipt


def _collect_judge_feedback_lines(x1d_judges: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {
        "synthesis": [],
        "jd_emphasis": [],
        "executive_signal": [],
    }
    for j in x1d_judges:
        if not (_is_model_backed_soft_fail(j) or j.get("decisive_failure")):
            continue
        blob = _judge_text_blob(j)
        tags = _taxonomy_tags(blob)
        provider = str(j.get("provider_name") or j.get("provider_key") or "judge")
        for finding in j.get("findings") or []:
            line = f"{provider}: {finding}"
            if "synthesis" in tags:
                out["synthesis"].append(line)
            if "jd_emphasis" in tags:
                out["jd_emphasis"].append(line)
            if "executive_signal" in tags:
                out["executive_signal"].append(line)
        for suggestion in j.get("remediation_suggestions") or []:
            line = f"{provider} remediation: {suggestion}"
            if "synthesis" in tags:
                out["synthesis"].append(line)
            elif "executive_signal" in tags or "jd_emphasis" in tags:
                out["synthesis"].append(line)
        for reason in j.get("fail_reasons") or []:
            out["synthesis"].append(f"{provider} fail_reason: {reason}")
        rationale = str(j.get("rationale") or "").strip()
        if rationale and _is_model_backed_soft_fail(j):
            out["synthesis"].append(f"{provider} rationale: {rationale[:400]}")
    return out


def _soft_failed_model_judges(x1d_judges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [j for j in x1d_judges if _is_model_backed_soft_fail(j)]


def _bounded_soft_fail_findings(x1d_judges: list[dict[str, Any]], *, max_lines: int = 4) -> list[str]:
    lines: list[str] = []
    for j in _soft_failed_model_judges(x1d_judges):
        provider = str(j.get("provider_name") or j.get("provider_key") or "judge")
        for finding in (j.get("findings") or [])[:2]:
            text = str(finding).strip()
            if text:
                lines.append(f"{provider}: {text[:240]}")
        if len(lines) >= max_lines:
            break
    return lines[:max_lines]


def snapshot_model_backed_judge_scores(x1d_judges: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-provider score snapshot for regen cycle monotonicity receipts."""
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        dimension_major_fail_on_judge,
    )

    providers: list[dict[str, Any]] = []
    for j in _normalize_judge_list(x1d_judges):
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        pk = str(j.get("provider_key") or j.get("judge_id") or "unknown")
        major_failed = [
            dim
            for dim in (
                "factual_support",
                "executive_signal",
                "resume_voice",
                "ats_alignment_without_keyword_stuffing",
                "anti_overfit",
                "synthesis_quality",
                "evidence_utilization",
                "deterministic_alignment",
            )
            if dimension_major_fail_on_judge(j, dim)
        ]
        providers.append(
            {
                "provider_key": pk,
                "score": j.get("score"),
                "normalized_score": j.get("normalized_score"),
                "pass": j.get("pass"),
                "provider_status": j.get("provider_status"),
                "major_failed_dimensions": major_failed,
            },
        )
    return {
        "schema": "executive_summary_judge_score_snapshot_v1",
        "providers": providers,
    }


def collect_judge_remediation_delta_lines(
    x1d_judges: list[dict[str, Any]],
    *,
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
    compact: bool | None = None,
) -> list[str]:
    """App-owned delta lines only (floors + output contract); core owns REGEN_DELTA/PROMPT_LOCK."""
    from agentic_core.L2_execution.regen.delta_shape_guard import estimate_token_count
    from agentic_core.L2_execution.regen.prompt_lock import (
        DEFAULT_MAX_DELTA_TOKENS,
        PROMPT_LOCK_GENERIC,
    )
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        collect_dimension_focused_regen_delta_lines,
        collect_dimension_remediation_lines,
        major_failed_dimension_ids_from_judges,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_judge_regen_connective_tissue_guard,
        format_judge_regen_mechanical_opener_guard,
        format_judge_regen_x2_floor,
        format_judge_remediation_synthesis_default,
    )

    if compact is None:
        compact = (
            judge_regen_prescriptive_delta_enabled()
            and not judge_regen_legacy_remediation_block_enabled()
        )

    soft_judges = _soft_failed_model_judges(x1d_judges)
    delta_parts: list[str] = []

    if compact:
        focused = collect_dimension_focused_regen_delta_lines(soft_judges)
        if focused:
            delta_parts.extend(f"- {ln}" for ln in focused[:4])
        else:
            delta_parts.append(
                "- synthesis_quality / executive_signal: rewrite S2–S6 as one connective SVP arc "
                "(no sequential achievement stack; jd_used_as_proof=false).",
            )
        if prior_word_count > 0 or prior_ledger_rows > 0:
            delta_parts.append(
                f"X2_FLOOR: ≥{max(1, prior_word_count)} words, ≥{max(1, prior_ledger_rows)} "
                "claim_ledger rows, exactly 6 sentences; preserve cited source_fact_ids.",
            )
        failed_dims = set(major_failed_dimension_ids_from_judges(soft_judges))
        if unused_fact_ids and "evidence_utilization" in failed_dims:
            preview = ", ".join(unused_fact_ids[:6])
            suffix = "..." if len(unused_fact_ids) > 6 else ""
            delta_parts.append(f"EVIDENCE_WEAVE (allowed ids only): {preview}{suffix}")
        delta_parts.append(format_judge_regen_connective_tissue_guard().strip())
        delta_parts.append(
            "OUTPUT: NEW JSON only; revise ONLY resume_display_text + claim_ledger; "
            "third person; jd_used_as_proof=false.",
        )
        joined = "\n".join(delta_parts)
        if estimate_token_count(joined) > DEFAULT_MAX_DELTA_TOKENS:
            delta_parts = [
                ln
                for ln in delta_parts
                if not ln.startswith("CONNECTIVE_TISSUE")
            ]
        _ = PROMPT_LOCK_GENERIC
        return delta_parts

    dimension_lines = collect_dimension_remediation_lines(soft_judges, min_fail_count=1)
    finding_lines = _bounded_soft_fail_findings(x1d_judges)

    if dimension_lines:
        delta_parts.extend(f"- {ln}" for ln in dimension_lines[:6])
    if finding_lines:
        delta_parts.extend(f"- finding: {ln}" for ln in finding_lines)

    if not delta_parts:
        delta_parts.append(
            f"- {format_judge_remediation_synthesis_default()}",
        )

    if prior_word_count > 0 or prior_ledger_rows > 0:
        delta_parts.append(
            format_judge_regen_x2_floor(
                prior_word_count=max(1, prior_word_count),
                prior_ledger_rows=max(1, prior_ledger_rows),
            ),
        )
        delta_parts.append(
            f"CLAIM_COVERAGE: preserve every source_fact_id from the prior claim_ledger "
            f"({prior_ledger_rows} rows minimum); do not drop allowed facts when rewriting prose.",
        )

    failed_dims = {ln.split(" ", 1)[0] for ln in dimension_lines}
    if unused_fact_ids and "evidence_utilization" in failed_dims:
        preview = ", ".join(unused_fact_ids[:8])
        suffix = "..." if len(unused_fact_ids) > 8 else ""
        delta_parts.append(
            f"EVIDENCE_WEAVE (allowed ids only, no new claims): {preview}{suffix}",
        )

    if allowed_fact_count >= 1:
        delta_parts.append(
            "Shape: exactly 6 sentences (max 140 words); same JSON schema as first turn.",
        )
    delta_parts.append(
        "X2_VOICE: No Additionally/Furthermore sentence openers; no unsupported "
        "regulated environments / governance framework / compliance / audit unless verbatim in cited facts.",
    )
    delta_parts.append(format_judge_regen_mechanical_opener_guard())
    delta_parts.append(
        "OUTPUT: Return a NEW complete JSON object (RAW JSON only; first char {, last char }). "
        "THIRD PERSON ONLY. No target company name in resume_display_text.",
    )
    delta_parts.append(
        "Revise ONLY resume_display_text and claim_ledger per JUDGE_DELTA; jd_used_as_proof=false.",
    )
    _ = PROMPT_LOCK_GENERIC  # apps import core lock text SSOT; envelope applied in format_regen_delta_user_turn
    return delta_parts


def build_judge_remediation_prescriptive_delta_message(
    *,
    x1d_judges: list[dict[str, Any]],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    prior_resume_display_text: str = "",
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
) -> str:
    """Surgical regen user turn via core ``format_regen_delta_user_turn`` (no duplicate PROMPT_LOCK block)."""
    from agentic_core.L2_execution.regen.prompt_lock import format_regen_delta_user_turn

    _ = prior_resume_display_text  # anchor lives on assistant turn when core runner is used
    lines = collect_judge_remediation_delta_lines(
        x1d_judges,
        unused_fact_ids=unused_fact_ids,
        allowed_fact_count=allowed_fact_count,
        prior_word_count=prior_word_count,
        prior_ledger_rows=prior_ledger_rows,
    )
    return format_regen_delta_user_turn(tuple(lines))


def build_judge_remediation_legacy_user_message(
    *,
    x1d_judges: list[dict[str, Any]],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    composition_plan: dict[str, Any] | None = None,
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
) -> str:
    feedback = _collect_judge_feedback_lines(x1d_judges)
    unused_note = ""
    if unused_fact_ids:
        preview = ", ".join(unused_fact_ids[:12])
        suffix = "..." if len(unused_fact_ids) > 12 else ""
        unused_note = (
            f"Unused allowed facts ({len(unused_fact_ids)}): {preview}{suffix}. "
            "Weave supported substance from these ids into claim_ledger rows — do not invent claims.\n"
        )
    prefer_five = ""
    if allowed_fact_count >= 6:
        prefer_five = "Shape: exactly 6 sentences (max 140 words); integrate additional allowed facts across the six-sentence arc.\n"
    else:
        prefer_five = "Shape: exactly 6 sentences (max 140 words); fit_to_evidence integrated narrative.\n"
    composition_note = ""
    plan = composition_plan or {}
    arc = plan.get("sentence_arc") or []
    if arc:
        arc_lines = []
        for row in arc[:6]:
            if isinstance(row, dict):
                idx = int(row.get("sentence_index") or 0)
                arc_lines.append(
                    f"S{idx + 1} ({row.get('arc_role')}): {row.get('guidance')}"
                )
        if arc_lines:
            composition_note += (
                "Follow six_sentence_arc (especially S3–S6 connective synthesis, no cert dump, no JD closer):\n"
                + "\n".join(f"- {ln}" for ln in arc_lines)
                + "\n"
            )
    if plan.get("dominant_arc") or plan.get("brushstroke_missing_ids"):
        missing = plan.get("brushstroke_missing_ids") or []
        composition_note = (
            f"COMPOSITION: dominant_arc={plan.get('dominant_arc')}; "
            f"weave missing brushstrokes {missing[:4]} using allowed facts only (no JD-as-proof).\n"
        )
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        collect_dimension_remediation_lines,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_judge_regen_connective_tissue_guard,
        format_judge_regen_mechanical_opener_guard,
        format_judge_regen_x2_floor,
        format_judge_remediation_synthesis_default,
    )

    dimension_lines = collect_dimension_remediation_lines(x1d_judges, min_fail_count=1)
    dimension_block = ""
    if dimension_lines:
        dimension_block = (
            "DIMENSION_VERDICTS (structured — prioritize these over free-text findings):\n"
            + "\n".join(f"- {ln}" for ln in dimension_lines[:8])
            + "\n"
        )

    x2_floor = ""
    if prior_word_count > 0 or prior_ledger_rows > 0:
        x2_floor = format_judge_regen_x2_floor(
            prior_word_count=max(1, prior_word_count),
            prior_ledger_rows=max(1, prior_ledger_rows),
        )

    return (
        "JUDGE_REMEDIATION (GRADE_ONLY feedback — do not invent facts):\n"
        f"{x2_floor}"
        f"{dimension_block}"
        f"- synthesis: {' | '.join(feedback['synthesis'][:6]) or format_judge_remediation_synthesis_default()}\n"
        f"- jd_emphasis: {' | '.join(feedback['jd_emphasis'][:4]) or 'shape emphasis from JD/briefing only; jd_used_as_proof=false'}\n"
        f"- executive_signal: {' | '.join(feedback['executive_signal'][:4]) or 'elevate SVP platform/governance/commercial signal from allowed facts'}\n"
        "- opener: technology strategy / enterprise technology executive (not narrow engineering-manager label) when TARGET_TITLE is SVP IT strategy.\n"
        "- NEVER name TARGET_COMPANY in resume_display_text (no 'at/for/with TargetCo', no 'align with TargetCo'); company is targeting-only.\n"
        f"{composition_note}"
        f"{unused_note}"
        f"{prefer_five}"
        "Integrate metrics into narrative; no Additionally/Furthermore; no credential dump.\n"
        "X2_PHRASE_GUARDS: do not use audit/compliance/governance-framework/regulated-enterprise "
        "wording unless the exact phrase appears in an allowed_fact_packet row you cite. "
        "No inferred bridge filler (proven track record, mission-critical, industry-leading, "
        "enterprise-wide transformation, strategic leader, market position) unless verbatim in cited facts.\n"
        "SYNTHESIS_SHAPE: S1 = one strategy thesis (no employer/credential opener stack); "
        "S3–S6 use connective causal prose (not bullet-stack); satisfy x2_executive_summary_synthesis_quality "
        "and x2_exec_summary_mechanical_opener_stack_zero.\n"
        f"{format_judge_regen_mechanical_opener_guard()}"
        f"{format_judge_regen_connective_tissue_guard()}"
        "FORBIDDEN PHRASES: \"with extensive experience\", \"with extensive experience in\", "
        "\"proven track record\", \"results-driven\", \"seasoned executive\" — use fact-backed outcomes.\n"
        "Do not echo JD/target-role keywords in resume_display_text; jd_used_as_proof must stay false.\n"
        "Do not pad for length; add substance only from allowed facts not yet cited in claim_ledger.\n"
        "Return a NEW complete JSON object (RAW JSON only; first char {, last char }). "
        "THIRD PERSON ONLY. Keep jd_used_as_proof=false."
    )


def build_judge_remediation_user_message(
    *,
    x1d_judges: list[dict[str, Any]],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    composition_plan: dict[str, Any] | None = None,
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
    prior_resume_display_text: str = "",
) -> str:
    if judge_regen_legacy_remediation_block_enabled():
        return build_judge_remediation_legacy_user_message(
            x1d_judges=x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_fact_count,
            composition_plan=composition_plan,
            prior_word_count=prior_word_count,
            prior_ledger_rows=prior_ledger_rows,
        )
    if judge_regen_prescriptive_delta_enabled():
        return build_judge_remediation_prescriptive_delta_message(
            x1d_judges=x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_fact_count,
            prior_resume_display_text=prior_resume_display_text,
            prior_word_count=prior_word_count,
            prior_ledger_rows=prior_ledger_rows,
        )
    return build_judge_remediation_legacy_user_message(
        x1d_judges=x1d_judges,
        unused_fact_ids=unused_fact_ids,
        allowed_fact_count=allowed_fact_count,
        composition_plan=composition_plan,
        prior_word_count=prior_word_count,
        prior_ledger_rows=prior_ledger_rows,
    )


def try_judge_safe_prefilter(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
    *,
    artifact_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """SRFS judge-safe repair stack removed (D1 purge). No-op for compatibility."""
    _ = (selected_facts, srfs_integration, artifact_dir)
    return parsed, None


def retry_qwen_for_judge_remediation(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    *,
    x1d_judges: list[dict[str, Any]],
    trigger_receipt: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    unused_fact_ids: list[str],
    composition_plan: dict[str, Any] | None = None,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
    max_attempts: int | None = None,
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
    cycle_index: int = 0,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Bounded post-judge same-authority regen (default one call per outer cycle)."""
    from apps_rg.runtime.sections.executive_summary_lane import (
        normalize_executive_summary_llm_output,
        parse_model_json,
        prune_exec_summary_claim_ledger_orphans,
        write_json,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_remediation_v1",
        "enabled": judge_regeneration_enabled(),
        "trigger": trigger_receipt,
        "accepted": False,
        "max_attempts": int(max_attempts if max_attempts is not None else judge_regen_max_attempts()),
        "attempts": [],
    }
    _attempt_cap = max(1, int(max_attempts if max_attempts is not None else 1))
    if not judge_regeneration_enabled():
        receipt["skipped"] = "judge_regen_disabled"
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_remediation_receipt.json", receipt)
        return raw_output, parsed, receipt

    from agentic_core.L2_execution.regen.prefix_digest import sha256_hex

    pre_parsed = dict(parsed)
    anchor_hash = sha256_hex(str(pre_parsed.get("resume_display_text") or "").strip())
    pre_parsed, prefilter_meta = try_judge_safe_prefilter(
        pre_parsed,
        list(selected_fact_plan.get("facts") or []),
        None,
        artifact_dir=artifact_dir,
    )
    if prefilter_meta:
        receipt["judge_safe_prefilter"] = prefilter_meta
        if prefilter_meta.get("repair_candidate_accepted") and not prefilter_meta.get("repair_unchanged"):
            parsed = pre_parsed
            raw_output = json.dumps(
                {k: v for k, v in parsed.items() if k != "selected_fact_plan"},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            receipt["prefilter_applied"] = True

    current_raw = raw_output
    current_parsed = parsed
    thread_messages = list(messages)
    allowed_count = len(allowed_fact_ids)

    anchor_text = str(current_parsed.get("resume_display_text") or "").strip()
    if judge_regen_legacy_remediation_block_enabled() or not judge_regen_prescriptive_delta_enabled():
        receipt["regen_user_message_mode"] = "legacy_remediation_block"
    else:
        receipt["regen_user_message_mode"] = "prescriptive_delta_v1"

    from apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge import (
        build_incremental_repair_contract,
        run_core_same_authority_regen,
    )
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        judge_regen_core_runner_enabled,
        judge_regen_max_attempts,
    )

    use_core_runner = (
        judge_regen_prescriptive_delta_enabled()
        and not judge_regen_legacy_remediation_block_enabled()
        and judge_regen_core_runner_enabled()
    )
    receipt["regen_engine"] = (
        "core.SameAuthorityRegenRunner" if use_core_runner else "apps_rg.thread_append"
    )
    # Reserve one extra iteration when core runner may refuse (e.g. delta_token_budget_exceeded).
    _loop_cap = _attempt_cap + 1 if use_core_runner else _attempt_cap

    for attempt in range(_loop_cap):
        if use_core_runner and attempt == 0:
            contract = build_incremental_repair_contract(
                messages=thread_messages,
                provider_payload=provider_payload,
                x1d_judges=x1d_judges,
                trigger_receipt=trigger_receipt,
                unused_fact_ids=unused_fact_ids,
                allowed_fact_count=allowed_count,
                anchor_output_text=anchor_text or current_raw,
                prior_word_count=prior_word_count,
                prior_ledger_rows=prior_ledger_rows,
                artifact_dir=artifact_dir,
                run_id=run_id,
                semantic_regen_attempt_index=attempt + 1,
                transport_retry_count=0,
                max_semantic_regen_attempts=judge_regen_max_attempts(),
            )
            regen_text, core_receipt, _sar, _chat_msgs = run_core_same_authority_regen(
                messages=thread_messages,
                provider_payload=provider_payload,
                contract=contract,
                artifact_dir=artifact_dir,
                run_id=run_id,
            )
            receipt["core_same_authority_regen"] = core_receipt
            attempt_record: dict[str, Any] = {
                "attempt": attempt + 1,
                "engine": "core.SameAuthorityRegenRunner",
                "accepted": bool(core_receipt.get("accepted")),
            }
            if not core_receipt.get("accepted"):
                attempt_record["skipped"] = core_receipt.get("refusal") or "refused"
                receipt["attempts"].append(attempt_record)
                receipt["core_runner_fallback"] = "apps_rg.thread_append"
                continue
            new_raw = regen_text
            new_parsed, new_err = parse_model_json(new_raw)
            attempt_record["parse_ok"] = bool(new_parsed)
            if new_parsed:
                new_parsed = normalize_executive_summary_llm_output(new_parsed, selected_fact_plan)
                prune_exec_summary_claim_ledger_orphans(new_parsed, allowed_fact_ids)
                from apps_rg.runtime.sections.executive_summary_voice_repair import (
                    apply_voice_repair_to_parsed,
                )

                new_parsed, voice_receipt = apply_voice_repair_to_parsed(
                    new_parsed,
                    selected_facts=list(selected_fact_plan.get("facts") or []),
                )
                if voice_receipt.get("repaired"):
                    receipt["voice_repair"] = voice_receipt
                current_raw = new_raw
                current_parsed = new_parsed
            else:
                attempt_record["parse_error"] = new_err
            receipt["attempts"].append(attempt_record)
            break

        repair_user = build_judge_remediation_user_message(
            x1d_judges=x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_count,
            composition_plan=composition_plan,
            prior_word_count=prior_word_count,
            prior_ledger_rows=prior_ledger_rows,
            prior_resume_display_text=anchor_text,
        )
        from apps_rg.runtime.sections.executive_summary_judge_regen_thread import (
            compact_judge_regen_messages,
        )
        from apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch import (
            budgeted_qwen_regen_call,
            mark_regen_call_parse,
        )

        thread_messages = [
            *thread_messages,
            {"role": "assistant", "content": current_raw},
            {"role": "user", "content": repair_user},
        ]
        thread_messages, compact_receipt = compact_judge_regen_messages(thread_messages)
        if compact_receipt.get("compacted"):
            receipt.setdefault("thread_compaction", []).append(compact_receipt)
        regen_outcome = budgeted_qwen_regen_call(
            provider_payload,
            messages=thread_messages,
            phase="judge_regen",
            call_site="retry_qwen_for_judge_remediation",
            cycle_index=int(cycle_index),
            attempt_index=attempt + 1,
            artifact_dir=artifact_dir,
            run_id=run_id,
        )
        result = regen_outcome.result
        attempt_record = {
            "attempt": attempt + 1,
            "engine": "apps_rg.thread_append",
            "call_id": regen_outcome.call_id,
            "dispatch_allowed": regen_outcome.dispatch_allowed,
            "block_reason": regen_outcome.block_reason,
        }
        if not regen_outcome.dispatch_allowed:
            attempt_record["skipped"] = "budget_blocked"
            attempt_record["status"] = "budget_blocked"
            receipt["attempts"].append(attempt_record)
            break
        if result is None or result.runtime_generation_status != "REAL_LLM":
            attempt_record["runtime_status"] = (
                result.runtime_generation_status if result is not None else "BLOCKED"
            )
            attempt_record["skipped"] = "non_real_llm"
            receipt["attempts"].append(attempt_record)
            break
        attempt_record["runtime_status"] = result.runtime_generation_status
        new_raw = result.raw_model_output
        new_parsed, new_err = parse_model_json(new_raw)
        attempt_record["parse_ok"] = bool(new_parsed)
        mark_regen_call_parse(artifact_dir, regen_outcome.call_id, parse_ok=bool(new_parsed))
        if new_parsed:
            new_parsed = normalize_executive_summary_llm_output(new_parsed, selected_fact_plan)
            prune_exec_summary_claim_ledger_orphans(new_parsed, allowed_fact_ids)
            from apps_rg.runtime.sections.executive_summary_voice_repair import apply_voice_repair_to_parsed

            new_parsed, voice_receipt = apply_voice_repair_to_parsed(
                new_parsed,
                selected_facts=list(selected_fact_plan.get("facts") or []),
            )
            if voice_receipt.get("repaired"):
                receipt["voice_repair"] = voice_receipt
            regen_text = str(new_parsed.get("resume_display_text") or "")
            attempt_record["regen_resume_word_count"] = len(re.findall(r"\S+", regen_text))
            current_raw = new_raw
            current_parsed = new_parsed
        else:
            attempt_record["parse_error"] = new_err
        receipt["attempts"].append(attempt_record)
        break

    post_hash = sha256_hex(str(current_parsed.get("resume_display_text") or "").strip())
    output_changed = bool(post_hash) and post_hash != anchor_hash
    llm_attempt_ok = any(
        (
            a.get("parse_ok")
            and a.get("dispatch_allowed", True)
            and a.get("skipped") != "budget_blocked"
        )
        or (a.get("engine") == "core.SameAuthorityRegenRunner" and a.get("accepted"))
        for a in receipt.get("attempts") or []
        if isinstance(a, dict)
    )
    receipt["anchor_output_hash"] = anchor_hash
    receipt["regen_output_hash"] = post_hash
    receipt["output_changed"] = output_changed
    receipt["accepted"] = output_changed and llm_attempt_ok and bool(
        current_parsed.get("resume_display_text"),
    )
    if any(
        isinstance(a, dict) and a.get("status") == "budget_blocked"
        for a in receipt.get("attempts") or []
    ):
        receipt["budget_blocked"] = True
    if artifact_dir is not None:
        write_json(artifact_dir / "judge_remediation_receipt.json", receipt)
    return current_raw, current_parsed, receipt


def repair_judge_regen_after_x2_fail(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    *,
    baseline_parsed: dict[str, Any],
    regen_raw: str,
    regen_parsed: dict[str, Any],
    failed_x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    strategy_executive: bool,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """One X2-aware repair pass on a judge-regen draft that failed deterministic gates.

    Uses the same synthesis-repair vocabulary and monotonicity guards as pre-X2 regen,
    anchored to the last X2-green baseline (not the failed regen candidate).
    """
    from apps_rg.runtime.sections.executive_summary_lane import (
        _build_synthesis_repair_user,
        normalize_executive_summary_llm_output,
        parse_model_json,
        prune_exec_summary_claim_ledger_orphans,
        write_json,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        failed_x2_gate_ids,
        format_x2_gate_failures_reject_reason,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_monotonic import (
        evaluate_synthesis_regen_monotonicity,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_regen_x2_repair_v1",
        "reject_reason": format_x2_gate_failures_reject_reason(failed_x2_gates),
        "baseline_word_count": len(
            re.findall(r"\S+", str(baseline_parsed.get("resume_display_text") or ""))
        ),
        "baseline_ledger_rows": len(list(baseline_parsed.get("claim_ledger") or [])),
        "regen_word_count": len(
            re.findall(r"\S+", str(regen_parsed.get("resume_display_text") or ""))
        ),
        "accepted": False,
    }
    reject_reason = str(receipt["reject_reason"])
    prior_wc = int(receipt["baseline_word_count"])
    prior_rows = int(receipt["baseline_ledger_rows"])
    repair_user = _build_synthesis_repair_user(
        reject_reason,
        attempt_index=0,
        prior_word_count=prior_wc,
        prior_ledger_rows=prior_rows,
        strategy_executive=strategy_executive,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_judge_regen_mechanical_opener_guard,
    )

    repair_user = (
        "JUDGE_REGEN_X2_REPAIR (fix deterministic gates while preserving judge-directed improvements):\n"
        f"{repair_user}\n"
        "Keep SVP synthesis arc (connective S3–S6); do not revert to bullet-stack metric inventory.\n"
        f"{format_judge_regen_mechanical_opener_guard()}"
        "Use active voice; vary sentence openers; S6 must cite ledger-backed substance (no generic capstone).\n"
    )
    repair_messages = [
        *list(messages),
        {"role": "assistant", "content": regen_raw or json.dumps(regen_parsed, ensure_ascii=False)},
        {"role": "user", "content": repair_user},
    ]
    from apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch import (
        budgeted_qwen_regen_call,
        mark_regen_call_parse,
    )

    regen_outcome = budgeted_qwen_regen_call(
        provider_payload,
        messages=repair_messages,
        phase="judge_x2_repair",
        call_site="repair_judge_regen_after_x2_fail",
        cycle_index=0,
        attempt_index=1,
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    receipt["call_id"] = regen_outcome.call_id
    receipt["dispatch_allowed"] = regen_outcome.dispatch_allowed
    receipt["block_reason"] = regen_outcome.block_reason
    if not regen_outcome.dispatch_allowed:
        receipt["skipped"] = "budget_blocked"
        receipt["status"] = "budget_blocked"
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_regen_x2_repair_receipt.json", receipt)
        return regen_raw, regen_parsed, receipt
    result = regen_outcome.result
    if result is None or result.runtime_generation_status != "REAL_LLM":
        receipt["skipped"] = "non_real_llm"
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_regen_x2_repair_receipt.json", receipt)
        return regen_raw, regen_parsed, receipt

    new_raw = result.raw_model_output
    new_parsed, parse_err = parse_model_json(new_raw)
    receipt["parse_ok"] = bool(new_parsed)
    mark_regen_call_parse(artifact_dir, regen_outcome.call_id, parse_ok=bool(new_parsed))
    if not new_parsed:
        receipt["parse_error"] = parse_err
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_regen_x2_repair_receipt.json", receipt)
        return regen_raw, regen_parsed, receipt

    new_parsed = normalize_executive_summary_llm_output(new_parsed, selected_fact_plan)
    prune_exec_summary_claim_ledger_orphans(new_parsed, allowed_fact_ids)
    from apps_rg.runtime.sections.executive_summary_voice_repair import apply_voice_repair_to_parsed

    from apps_rg.runtime.sections.executive_summary_judge_regen_loop import (
        prepare_parsed_after_judge_regen,
    )

    new_parsed, prepare_receipt = prepare_parsed_after_judge_regen(
        new_parsed,
        allowed_fact_ids=allowed_fact_ids,
        plan_facts=list(selected_fact_plan.get("facts") or []),
        artifact_dir=artifact_dir,
    )
    receipt["prepare_after_repair"] = prepare_receipt
    _failed_gate_id_set = failed_x2_gate_ids(failed_x2_gates)
    receipt["failed_gate_ids"] = sorted(_failed_gate_id_set)
    mono_ok, mono_detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=baseline_parsed,
        prior_reject_reason=reject_reason,
        new_parsed=new_parsed,
        failed_gate_ids=_failed_gate_id_set,
        repair_context="judge_x2_repair",
    )
    receipt["monotonicity"] = mono_detail
    if not mono_ok:
        receipt["rejected"] = "monotonicity"
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_regen_x2_repair_receipt.json", receipt)
        return regen_raw, regen_parsed, receipt

    receipt["accepted"] = bool(
        new_parsed
        and regen_outcome.dispatch_allowed
        and result.runtime_generation_status == "REAL_LLM"
        and not regen_outcome.call_record.get("transport_timeout")
    )
    receipt["repaired_word_count"] = len(
        re.findall(r"\S+", str(new_parsed.get("resume_display_text") or ""))
    )
    receipt["repaired_ledger_rows"] = len(list(new_parsed.get("claim_ledger") or []))
    if artifact_dir is not None:
        write_json(artifact_dir / "judge_regen_x2_repair_receipt.json", receipt)
    return new_raw, new_parsed, receipt


def rerun_x2_after_judge_remediation(
    *,
    resume_display_text: str,
    parsed_for_x2: dict[str, Any],
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any],
    allowed_fact_ids: set[str],
    args: Any,
    jd_text: str,
    temperature: float,
    runtime_generation_status: str,
    artifact_dir: Path,
    model_name: str | None,
    prompt_hash: str,
    compiled_prompt: str | None,
    raw_output: str,
    selected_facts: list[dict[str, Any]],
    x1d_judges: list[dict[str, Any]],
    proof_pool_metadata: dict[str, Any] | None,
    proof_pool_ref: str,
    proof_pool_digest: str,
) -> list[dict[str, Any]]:
    gates = run_x2_gates(
        resume_display_text=resume_display_text,
        parsed_output=parsed_for_x2,
        claim_ledger=claim_ledger,
        text_claim_coverage=text_claim_coverage,
        allowed_fact_ids=allowed_fact_ids,
        target_company=str(args.target_company),
        jd_text=str(jd_text or ""),
        temperature=temperature,
        runtime_generation_status=runtime_generation_status,
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        artifacts_dir=artifact_dir,
        provider_requested=str(args.provider),
        provider_attempted=str(args.provider),
        model_name=model_name,
        prompt_hash=prompt_hash,
        compiled_prompt=compiled_prompt,
        raw_output=raw_output,
        target_role=getattr(args, "target_role", None),
        selected_facts=selected_facts,
        x1d_judges=x1d_judges,
        proof_pool_metadata=proof_pool_metadata,
        proof_pool_ref=proof_pool_ref,
        proof_pool_digest=proof_pool_digest,
    )
    return [g.to_dict() for g in gates]


def rerun_soft_failed_judges(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    judge_packet: dict[str, Any],
    judge_packet_ref: str,
    compiled_prompt: str | None,
    artifact_dir: Path,
    judge_keys: list[str],
    judge_mode: str,
    prior_judges: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]] | None = None,
    allowed_fact_packet: list[dict[str, Any]] | None = None,
    allowed_fact_ids: set[str] | None = None,
    target_title: str = "",
    target_company: str = "",
    jd_text: str = "",
    briefing_text: str = "",
    parsed_output: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Re-run only model-backed soft-failed judges after remediation.

    When *x2_gates* is set, rebuild the post-X2 judge packet (same authority as
    ``refresh_x1d_judges_after_full_x2``) so soft reruns do not regress to the
    pre-X2 packet hash.
    """
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        build_deterministic_gate_summary,
        build_deterministic_gate_summary_from_x2_gates,
        build_executive_summary_judge_packet,
        write_executive_summary_judge_packet,
    )
    from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges

    soft_keys = {
        str(j.get("provider_key"))
        for j in prior_judges
        if j.get("provider_key") and _is_model_backed_soft_fail(j)
    }
    if not soft_keys:
        return list(prior_judges)

    packet_ref = judge_packet_ref
    rescore_full_panel = False
    if x2_gates is not None and allowed_fact_packet is not None and allowed_fact_ids is not None:
        gate_summary = build_deterministic_gate_summary_from_x2_gates(x2_gates)
        packet = build_executive_summary_judge_packet(
            resume_display_text=resume_display_text,
            claim_ledger=claim_ledger,
            allowed_fact_packet=allowed_fact_packet,
            allowed_fact_ids=allowed_fact_ids,
            target_title=target_title,
            target_company=target_company,
            jd_text=jd_text,
            briefing_text=briefing_text,
            parsed_output=parsed_output,
            deterministic_gate_summary=gate_summary,
        )
        packet_ref = write_executive_summary_judge_packet(
            artifact_dir / "executive_summary_judge_packet_post_x2.json",
            packet,
        )
        from apps_rg.runtime.judges.executive_summary_judge_packet import judge_packet_hash

        new_packet_hash = judge_packet_hash(packet)
        prior_model_hashes = {
            str(j.get("judge_packet_hash") or j.get("input_hash") or "").strip()
            for j in prior_judges
            if isinstance(j, dict)
            and str(j.get("evaluator_mode") or "") == "MODEL_BACKED"
            and not j.get("provider_blocked")
        } - {""}
        if prior_model_hashes and new_packet_hash not in prior_model_hashes:
            rescore_full_panel = True
    else:
        packet = dict(judge_packet)
        packet["deterministic_gate_summary"] = build_deterministic_gate_summary(
            resume_display_text=resume_display_text,
            parsed_output={"resume_display_text": resume_display_text, "claim_ledger": claim_ledger},
            claim_ledger=claim_ledger,
            allowed_fact_ids=set(packet.get("allowed_fact_ids") or []),
        )
        packet["candidate_output"] = {
            "resume_display_text": resume_display_text,
            "claim_ledger": claim_ledger,
        }
    keys_to_run = list(judge_keys) if rescore_full_panel else [k for k in judge_keys if k in soft_keys]
    if not keys_to_run:
        return list(prior_judges)

    refreshed: dict[str, dict[str, Any]] = {}
    for raw_j in run_llm_judges(
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        judge_keys=keys_to_run,
        mode=judge_mode,
        artifact_base=artifact_dir,
        judge_packet=packet,
        judge_packet_ref=packet_ref,
        compiled_prompt=compiled_prompt,
    ):
        jd = _coerce_judge_dict(raw_j)
        pk = str(jd.get("provider_key") or "")
        if pk:
            refreshed[pk] = jd
    out: list[dict[str, Any]] = []
    for j in _normalize_judge_list(prior_judges):
        pk = str(j.get("provider_key") or "")
        if pk in refreshed:
            out.append(refreshed[pk])
        else:
            out.append(j)
    return out


def rescore_judges_after_regen(
    *,
    x2_gates: list[dict[str, Any]],
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_packet: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing_text: str,
    parsed_output: dict[str, Any] | None,
    judge_keys: list[str],
    judge_mode: str,
    artifact_dir: Path,
    compiled_prompt: str | None,
    prior_judges: list[dict[str, Any]],
    judge_packet: dict[str, Any],
    judge_packet_ref: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Post-regen judge spend: soft-failed only by default (not full 3-judge panel)."""
    mode = post_regen_judge_rescore_mode()
    if mode == POST_REGEN_JUDGE_RESCORE_FULL_PANEL:
        refreshed, receipt = refresh_x1d_judges_after_full_x2(
            x2_gates=x2_gates,
            resume_display_text=resume_display_text,
            claim_ledger=claim_ledger,
            allowed_fact_packet=allowed_fact_packet,
            allowed_fact_ids=allowed_fact_ids,
            target_title=target_title,
            target_company=target_company,
            jd_text=jd_text,
            briefing_text=briefing_text,
            parsed_output=parsed_output,
            judge_keys=judge_keys,
            judge_mode=judge_mode,
            artifact_dir=artifact_dir,
            compiled_prompt=compiled_prompt,
            prior_judges=prior_judges,
        )
        receipt["rescore_mode"] = POST_REGEN_JUDGE_RESCORE_FULL_PANEL
        return refreshed, receipt

    soft_keys = {
        str(j.get("provider_key"))
        for j in prior_judges
        if j.get("provider_key") and _is_model_backed_soft_fail(j)
    }
    scores_before = snapshot_model_backed_judge_scores(prior_judges)
    out = rerun_soft_failed_judges(
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        judge_packet=judge_packet,
        judge_packet_ref=judge_packet_ref,
        compiled_prompt=compiled_prompt,
        artifact_dir=artifact_dir,
        judge_keys=judge_keys,
        judge_mode=judge_mode,
        prior_judges=prior_judges,
        x2_gates=x2_gates,
        allowed_fact_packet=allowed_fact_packet,
        allowed_fact_ids=allowed_fact_ids,
        target_title=target_title,
        target_company=target_company,
        jd_text=jd_text,
        briefing_text=briefing_text,
        parsed_output=parsed_output,
    )
    scores_after = snapshot_model_backed_judge_scores(out)
    deltas: list[dict[str, Any]] = []
    before_by_key = {
        str(row.get("provider_key")): row
        for row in scores_before.get("providers") or []
        if isinstance(row, dict)
    }
    for row in scores_after.get("providers") or []:
        if not isinstance(row, dict):
            continue
        pk = str(row.get("provider_key") or "")
        if pk not in soft_keys:
            continue
        prev = before_by_key.get(pk) or {}
        try:
            prev_ns = float(prev.get("normalized_score")) if prev.get("normalized_score") is not None else None
            next_ns = float(row.get("normalized_score")) if row.get("normalized_score") is not None else None
        except (TypeError, ValueError):
            prev_ns = next_ns = None
        delta_ns = None
        if prev_ns is not None and next_ns is not None:
            delta_ns = round(next_ns - prev_ns, 4)
        deltas.append(
            {
                "provider_key": pk,
                "normalized_score_before": prev_ns,
                "normalized_score_after": next_ns,
                "normalized_score_delta": delta_ns,
                "pass_before": prev.get("pass"),
                "pass_after": row.get("pass"),
                "improved": delta_ns is not None and delta_ns > 0,
            },
        )
    return out, {
        "schema": "executive_summary_post_regen_judge_rescore_v1",
        "rescore_mode": POST_REGEN_JUDGE_RESCORE_SOFT_ONLY,
        "soft_failed_provider_keys": sorted(soft_keys),
        "judges_rescored_count": len(soft_keys),
        "scores_before": scores_before,
        "scores_after": scores_after,
        "score_deltas": deltas,
    }


def refresh_x1d_judges_after_full_x2(
    *,
    x2_gates: list[dict[str, Any]],
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_packet: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing_text: str,
    parsed_output: dict[str, Any] | None,
    judge_keys: list[str],
    judge_mode: str,
    artifact_dir: Path,
    compiled_prompt: str | None,
    prior_judges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Re-grade with authoritative full-X2 deterministic_gate_summary (post-X2 refresh)."""
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        build_deterministic_gate_summary_from_x2_gates,
        build_executive_summary_judge_packet,
        write_executive_summary_judge_packet,
    )
    from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges

    receipt: dict[str, Any] = {
        "schema": "executive_summary_post_x2_x1d_refresh_v1",
        "enabled": post_x2_judge_refresh_enabled(),
        "prior_scores": {
            str(j.get("provider_key")): j.get("score") for j in prior_judges if j.get("provider_key")
        },
    }
    if not post_x2_judge_refresh_enabled():
        receipt["skipped"] = "post_x2_refresh_disabled"
        return list(prior_judges), receipt

    gate_summary = build_deterministic_gate_summary_from_x2_gates(x2_gates)
    packet = build_executive_summary_judge_packet(
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        allowed_fact_packet=allowed_fact_packet,
        allowed_fact_ids=allowed_fact_ids,
        target_title=target_title,
        target_company=target_company,
        jd_text=jd_text,
        briefing_text=briefing_text,
        parsed_output=parsed_output,
        deterministic_gate_summary=gate_summary,
    )
    packet_ref = write_executive_summary_judge_packet(
        artifact_dir / "executive_summary_judge_packet_post_x2.json",
        packet,
    )
    refreshed = [
        j.to_dict()
        for j in run_llm_judges(
            resume_display_text=resume_display_text,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            mode=judge_mode,
            artifact_base=artifact_dir,
            judge_packet=packet,
            judge_packet_ref=packet_ref,
            compiled_prompt=compiled_prompt,
        )
    ]
    receipt["refreshed_scores"] = {
        str(j.get("provider_key")): j.get("score") for j in refreshed if j.get("provider_key")
    }
    receipt["gate_summary_gate_count"] = len(gate_summary)
    receipt["judge_packet_post_x2_ref"] = packet_ref
    return refreshed, receipt

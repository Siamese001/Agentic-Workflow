"""HOP8 qa_report — scorecard + compliance annotations.

Consumes the draft, validation report, and evidence bundle; emits a
``qa_report`` dict with a composite quality score and per-dimension
breakdown. The integration stage (HOP9) folds this into the final
``GovernedLicE2ERunRecord``.
"""

from __future__ import annotations

import re
from typing import Any

from apps_lic.policy.reasoning_intensity import (
    JUDGE_CANDIDATE_SELECTION,
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    JUDGE_SAFETY_NO_FABRICATION,
    JUDGE_SCHEMA_POLICY_NO_SEND,
    compact_policy,
    default_reasoning_policy,
)


class QaReportEngine:
    """Composite scorecard over validation + evidence coverage."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        draft = context.get("draft_message") or {}
        report = context.get("validation_report") or {}
        evidence = context.get("evidence_bundle") or {}
        policy = compact_policy(
            context.get("reasoning_policy")
            or draft.get("reasoning_policy")
            or report.get("reasoning_policy")
            or default_reasoning_policy()
        )
        judge_scores, judge_refs, x2_gate_summary, x1d_outputs = _run_targeted_judges(
            draft=draft,
            report=report,
            evidence=evidence,
            policy=policy,
        )

        validation_score = 1.0 if report.get("passed") else 0.4
        grounding_score = (
            1.0
            if evidence.get("support_status") == "PASS" or evidence.get("count", 0) >= 3
            else 0.5
            if evidence.get("count", 0) > 0
            else 0.0
        )
        structural_score = 0.0 if report.get("issues") else 1.0
        judge_quality_score = _judge_quality_score(judge_scores)

        composite = round(
            0.30 * validation_score
            + 0.20 * grounding_score
            + 0.20 * structural_score
            + 0.30 * judge_quality_score,
            3,
        )

        return {
            "qa_report": {
                "composite_score": composite,
                "validation_score": validation_score,
                "grounding_score": grounding_score,
                "structural_score": structural_score,
                "judge_quality_score": judge_quality_score,
                "reasoning_policy": policy,
                "sc_level": policy["sc_level"],
                "reasoning_intensity": policy["reasoning_intensity"],
                "judge_profile": policy["judge_profile"],
                "active_judges": list(policy["judges"]),
                "judge_count": len(policy["judges"]),
                "judge_scores": judge_scores,
                "judge_evidence_refs": judge_refs,
                "x2_deterministic_gates": list(policy["x2_deterministic_gates"]),
                "x2_deterministic_gate_count": len(policy["x2_deterministic_gates"]),
                "x2_gate_summary": x2_gate_summary,
                "x2_gates_passed": _x2_gates_passed(report, x2_gate_summary),
                "x1d_llm_judges": list(policy["x1d_llm_judges"]),
                "x1d_llm_judge_count": len(policy["x1d_llm_judges"]),
                "x1d_llm_judge_outputs": x1d_outputs,
                "x1d_model_backed_pass": _x1d_model_backed_pass(x1d_outputs),
                "quality_contract": {
                    "generation_temperature": draft.get("generation_temperature"),
                    "top_p": draft.get("top_p"),
                    "self_consistency_samples": int(policy["max_candidates"]),
                    "sc_level": policy["sc_level"],
                    "reasoning_intensity": policy["reasoning_intensity"],
                    "judge_profile": policy["judge_profile"],
                    "active_judges": list(policy["judges"]),
                    "judge_count": len(policy["judges"]),
                    "x2_deterministic_gates": list(policy["x2_deterministic_gates"]),
                    "x2_deterministic_gate_count": len(policy["x2_deterministic_gates"]),
                    "x2_gates_passed": _x2_gates_passed(report, x2_gate_summary),
                    "x1d_llm_judges": list(policy["x1d_llm_judges"]),
                    "x1d_llm_judge_count": len(policy["x1d_llm_judges"]),
                    "x1d_runs_after_x2": bool(policy.get("x1d_runs_after_x2", True)),
                    "x1d_max_attempts": int(policy.get("x1d_max_attempts", 1) or 1),
                    "x1d_failure_policy": str(policy.get("x1d_failure_policy", "")),
                    "x1d_model_backed_pass": _x1d_model_backed_pass(x1d_outputs),
                    "max_candidates": int(policy["max_candidates"]),
                    "candidate_count": int(draft.get("candidate_count") or 0),
                    "validation_repair_passes": int(
                        policy.get("validation_repair_passes", 1) or 0
                    ),
                    "generation_attempts": draft.get("attempts", 1),
                    "max_generation_attempts": draft.get("max_generation_attempts", 1),
                    "x1_x2_x3_exit_retries": 0,
                    "retry_policy": "one_exit_decision_no_x_retry",
                    "fail_closed_on_empty_evidence": bool(
                        policy.get("fail_closed_on_empty_evidence", True)
                    ),
                    "no_send_authority": bool(policy.get("no_send_authority", True)),
                },
                "generator": draft.get("generator", "unknown"),
                "provider_profile": draft.get("provider_profile", ""),
                "model": draft.get("model", ""),
                "evidence_count": int(evidence.get("count", 0)),
                "evidence_support_status": str(evidence.get("support_status", "") or ""),
                "issues": list(report.get("issues") or []),
            },
        }


def _run_targeted_judges(
    *,
    draft: dict[str, Any],
    report: dict[str, Any],
    evidence: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[
    dict[str, float],
    dict[str, list[str]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    scores: dict[str, float] = {}
    refs: dict[str, list[str]] = {}
    x2_gate_summary: dict[str, dict[str, Any]] = {}
    # X1D semantic judging is owned by the independent Claude Exit path
    # (validation_exit + x1d_gpt_judge_adapter). The HOP8 scorecard never
    # calls an LLM judge; provider-backed X1D judging is owned by Exit.
    x1d_outputs: dict[str, dict[str, Any]] = {}

    for judge_name in policy.get("x2_deterministic_gates", ()):
        score, evidence_refs = _score_dimension(judge_name, draft, report, evidence, policy)
        scores[str(judge_name)] = round(float(score), 3)
        refs[str(judge_name)] = list(evidence_refs)
        threshold = _x2_gate_threshold(str(judge_name))
        x2_gate_summary[str(judge_name)] = {
            "score": round(float(score), 3),
            "threshold": threshold,
            "pass": float(score) >= threshold,
            "evidence_refs": list(evidence_refs),
            "authority": "x2_deterministic_gate",
        }

    if bool(policy.get("x1d_enabled", True)):
        for judge_name in policy.get("x1d_llm_judges", ()):
            # Originality is graded only by the live GPT X1D judge at Exit,
            # not in this deterministic scorecard.
            if judge_name == JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D:
                continue
            score, evidence_refs = _score_dimension(judge_name, draft, report, evidence, policy)
            scores[str(judge_name)] = round(float(score), 3)
            refs[str(judge_name)] = list(evidence_refs)
    return scores, refs, x2_gate_summary, x1d_outputs


def _score_dimension(
    judge_name: str,
    draft: dict[str, Any],
    report: dict[str, Any],
    evidence: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[float, list[str]]:
    """Deterministic proxy score for one quality dimension."""
    if judge_name == JUDGE_SCHEMA_POLICY_NO_SEND:
        return _judge_schema_policy_no_send(draft, report, policy)
    if judge_name == JUDGE_LINKEDIN_TONE:
        return _judge_linkedin_tone(draft)
    if judge_name == JUDGE_EVIDENCE_SUPPORT:
        return _judge_evidence_support(draft, evidence)
    if judge_name == JUDGE_SAFETY_NO_FABRICATION:
        return _judge_safety_no_fabrication(draft, report, policy)
    if judge_name == JUDGE_CANDIDATE_SELECTION:
        return _judge_candidate_selection(draft, policy)
    return 0.0, [f"unknown_judge:{judge_name}"]


def _judge_schema_policy_no_send(
    draft: dict[str, Any],
    report: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[float, list[str]]:
    text = str(draft.get("message_text") or draft.get("body") or "")
    refs: list[str] = []
    score = 1.0
    if draft.get("channel") != "linkedin":
        score -= 0.35
        refs.append("channel_not_linkedin")
    if len(text) > 600 or len(text) < 20:
        score -= 0.25
        refs.append("message_length_out_of_contract")
    if report.get("issues"):
        score -= 0.30
        refs.append("validation_issues_present")
    if not bool(policy.get("no_send_authority", True)):
        score -= 0.40
        refs.append("no_send_authority_false")
    return max(0.0, score), refs or ["schema_policy_no_send_clean"]


def _judge_linkedin_tone(draft: dict[str, Any]) -> tuple[float, list[str]]:
    text = str(draft.get("message_text") or draft.get("body") or "")
    lowered = text.lower()
    score = 1.0
    refs: list[str] = []
    if not text.startswith("Hi "):
        score -= 0.20
        refs.append("linkedin_salutation_missing")
    if not _has_low_friction_ask(lowered):
        score -= 0.30
        refs.append("low_friction_ask_missing")
    if _has_generic_phrase(lowered):
        score -= 0.35
        refs.append("generic_outreach_phrase")
    if "—" in text:
        score -= 0.15
        refs.append("em_dash_present")
    return max(0.0, score), refs or ["linkedin_tone_channel_clean"]


def _judge_evidence_support(
    draft: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[float, list[str]]:
    support_status = str(evidence.get("support_status", "") or "").upper()
    unsupported = list(draft.get("unsupported_claims") or [])
    refs: list[str] = []
    score = 1.0
    if support_status in {"WEAK", "EMPTY"}:
        score -= 0.60
        refs.append(f"c0_support_{support_status.lower()}")
    if unsupported:
        score -= 0.40
        refs.append("unsupported_claims_present")
    return max(0.0, score), refs or ["claims_supported_by_c0"]


def _judge_safety_no_fabrication(
    draft: dict[str, Any],
    report: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[float, list[str]]:
    refs: list[str] = []
    score = 1.0
    issues = set(report.get("issues") or [])
    if any("unverified_candidate_metric" in issue for issue in issues):
        score -= 0.40
        refs.append("unverified_candidate_metric")
    if draft.get("unsupported_claims"):
        score -= 0.40
        refs.append("unsupported_claims_present")
    if not bool(policy.get("no_send_authority", True)):
        score -= 0.30
        refs.append("no_send_authority_false")
    return max(0.0, score), refs or ["safety_no_fabrication_clean"]


def _judge_candidate_selection(
    draft: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[float, list[str]]:
    max_candidates = int(policy.get("max_candidates", 1) or 1)
    candidate_count = int(draft.get("candidate_count") or 1)
    if candidate_count <= 0:
        return 0.0, ["no_candidate_returned"]
    if candidate_count > max_candidates:
        return 0.0, ["candidate_count_exceeds_policy"]
    return 1.0, [f"candidate_count={candidate_count}:max_candidates={max_candidates}"]


def _judge_quality_score(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores.values()) / len(scores), 3)


def _x2_gate_threshold(gate_name: str) -> float:
    if gate_name == JUDGE_LINKEDIN_TONE:
        return 0.65
    if gate_name == JUDGE_CANDIDATE_SELECTION:
        return 1.0
    return 0.80


def _x2_gates_passed(report: dict[str, Any], summary: dict[str, dict[str, Any]]) -> bool:
    if not report.get("passed"):
        return False
    if not summary:
        return False
    return all(bool(item.get("pass")) for item in summary.values())


def _x1d_model_backed_pass(outputs: dict[str, dict[str, Any]]) -> bool:
    if not outputs:
        return False
    return any(
        out.get("evaluator_mode") == "MODEL_BACKED" and out.get("pass") is True
        for out in outputs.values()
    )


def _has_low_friction_ask(lowered: str) -> bool:
    return any(
        token in lowered
        for token in (
            "chat",
            "call",
            "conversation",
            "connect",
            "resume review",
            "worth a brief",
            "worth a short",
            "open to",
        )
    )


def _has_generic_phrase(lowered: str) -> bool:
    return bool(
        re.search(
            r"\b(potential synergies|i noticed your role|i believe my background aligns|given your expertise)\b",
            lowered,
        )
    )

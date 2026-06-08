"""HOP8 qa_report — scorecard + compliance annotations.

Consumes the draft, validation report, and evidence bundle; emits a
``qa_report`` dict with a composite quality score and per-dimension
breakdown. The integration stage (HOP9) folds this into the final
``GovernedLicE2ERunRecord``.
"""

from __future__ import annotations

from typing import Any

from apps_lic.engines.judges.antipattern_clean_judge import AntipatternCleanJudge
from apps_lic.engines.judges.ask_friction_judge import AskFrictionJudge
from apps_lic.engines.judges.asymmetric_insight_judge import AsymmetricInsightJudge
from apps_lic.engines.judges.brand_voice_judge import BrandVoiceJudge
from apps_lic.engines.judges.personalization_judge import PersonalizationJudge
from apps_lic.engines.judges.proof_appropriate_judge import ProofAppropriateJudge
from apps_lic.engines.judges.response_likelihood_judge import ResponseLikelihoodJudge


class QaReportEngine:
    """Composite scorecard over validation + evidence coverage."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        draft = context.get("draft_message") or {}
        report = context.get("validation_report") or {}
        evidence = context.get("evidence_bundle") or {}
        judge_scores, judge_refs = _run_quality_judges(draft)

        validation_score = 1.0 if report.get("passed") else 0.4
        grounding_score = 1.0 if evidence.get("count", 0) >= 3 else 0.5 if evidence.get("count", 0) > 0 else 0.0
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
                "judge_scores": judge_scores,
                "judge_evidence_refs": judge_refs,
                "quality_contract": {
                    "generation_temperature": draft.get("generation_temperature"),
                    "top_p": draft.get("top_p"),
                    "self_consistency_samples": 1,
                    "generation_attempts": draft.get("attempts", 1),
                    "max_generation_attempts": draft.get("max_generation_attempts", 1),
                    "x1_x2_x3_exit_retries": 0,
                    "retry_policy": "one_shot_fail_closed",
                },
                "generator": draft.get("generator", "unknown"),
                "provider_profile": draft.get("provider_profile", ""),
                "model": draft.get("model", ""),
                "evidence_count": int(evidence.get("count", 0)),
                "issues": list(report.get("issues") or []),
            },
        }


def _run_quality_judges(draft: dict[str, Any]) -> tuple[dict[str, float], dict[str, list[str]]]:
    text = str(draft.get("message_text") or draft.get("body") or "")
    recipient_class = str(draft.get("recipient_category") or draft.get("recipient_class") or "").upper()
    run_context = {
        "output": {"text": text},
        "recipient_class": recipient_class,
        "outreach_mode": "cold",
        "voice_profile": {"register": draft.get("register", "professional")},
    }
    judges = {
        "response_likelihood": ResponseLikelihoodJudge(),
        "brand_voice": BrandVoiceJudge(),
        "personalization": PersonalizationJudge(),
        "proof_appropriate": ProofAppropriateJudge(),
        "asymmetric_insight": AsymmetricInsightJudge(),
        "ask_friction": AskFrictionJudge(),
        "antipattern_clean": AntipatternCleanJudge(),
    }
    scores: dict[str, float] = {}
    refs: dict[str, list[str]] = {}
    for name, judge in judges.items():
        score, evidence_refs = judge.grade(None, run_context)
        if isinstance(score, (int, float)):
            scores[name] = round(float(score), 3)
        refs[name] = list(evidence_refs or [])
    return scores, refs


def _judge_quality_score(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    ask_friction = 1.0 - min(1.0, max(0.0, scores.get("ask_friction", 1.0)))
    components = [
        scores.get("response_likelihood", 0.0),
        scores.get("brand_voice", 0.0),
        scores.get("personalization", 0.0),
        scores.get("proof_appropriate", 0.0),
        scores.get("asymmetric_insight", 0.0),
        scores.get("antipattern_clean", 0.0),
        ask_friction,
    ]
    return round(sum(components) / len(components), 3)

"""Unit tests for the W3 deterministic Judge evaluators.

Covers `apps_lic.policy.judge_evaluators`:
  - evaluate_hop1_llm_fallback (W3-P1)
  - evaluate_hop2_grounding    (W3-P2)
  - evaluate_hop8_narrative    (W3-P3)

Each evaluator is tested standalone (returns the right tuple shape +
score behavior) and end-to-end via JudgeBase (rubric resolves the
score band -> X3 disposition correctly).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_lic.policy.judge_base import JudgeBase, Rubric
from apps_lic.policy.judge_evaluators import (
    evaluate_hop1_llm_fallback,
    evaluate_hop2_grounding,
    evaluate_hop8_narrative,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
RUBRIC_DIR = REPO_ROOT / "apps_lic" / "policy" / "rubrics"


# ---------------------------------------------------------------------- #
# HOP1 LLM-fallback evaluator
# ---------------------------------------------------------------------- #


def _hop1_rubric() -> Rubric:
    return Rubric.load(RUBRIC_DIR / "judge_hop1_classifier.yaml")


def test_hop1_strong_when_high_confidence_and_grounded_reasoning():
    state = {
        "title": "Senior Vice President of Engineering",
        "archetype": "VP",
        "confidence": 0.85,
        "reasoning": "Title contains 'engineering' and 'president' indicating VP archetype",
    }
    score, codes, refs, hint = evaluate_hop1_llm_fallback(state, _hop1_rubric())
    assert score >= 0.75, f"expected STRONG band, got {score}"
    assert "confidence_below_floor" not in codes
    assert hint == ""


def test_hop1_weak_when_reasoning_does_not_cite_title():
    state = {
        "title": "Chief Technology Officer at Acme Corp",
        "archetype": "OTHER",
        "confidence": 0.30,
        "reasoning": "based on intuition this looks like nothing in particular",
    }
    score, codes, refs, hint = evaluate_hop1_llm_fallback(state, _hop1_rubric())
    assert score < 0.50
    assert "confidence_below_floor" in codes
    assert "reasoning_does_not_reference_title" in codes
    assert hint  # non-empty remediation hint


def test_hop1_raises_on_missing_title():
    with pytest.raises(ValueError, match="title missing"):
        evaluate_hop1_llm_fallback({"title": ""}, _hop1_rubric())


def test_hop1_judge_end_to_end_strong_routes_allow():
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop1_classifier.yaml",
        evaluate_fn=evaluate_hop1_llm_fallback,
    )
    sc = judge.judge(
        {
            "title": "Vice President of Product Engineering",
            "archetype": "VP",
            "confidence": 0.85,
            "reasoning": "Title contains 'vice president' and 'engineering' VP indicators",
        },
        emit_marker=False,
    )
    assert sc.x3_disposition == "ALLOW"
    assert sc.judge_name == "HOP1_LLMFallbackClassifier"


def test_hop1_judge_end_to_end_weak_routes_hitl():
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop1_classifier.yaml",
        evaluate_fn=evaluate_hop1_llm_fallback,
    )
    sc = judge.judge(
        {
            "title": "Chief Revenue Officer",
            "archetype": "OTHER",
            "confidence": 0.20,
            "reasoning": "guess",
        },
        emit_marker=False,
    )
    # judge_disposition_policy: weak_band_hop1_llm_fallback -> HITL
    assert sc.x3_disposition == "HITL"


# ---------------------------------------------------------------------- #
# HOP2 grounding evaluator
# ---------------------------------------------------------------------- #


def _hop2_rubric() -> Rubric:
    return Rubric.load(RUBRIC_DIR / "judge_hop2_grounding.yaml")


def test_hop2_strong_when_brief_cites_evidence():
    state = {
        "strategic_brief": (
            "AcmeCorp launched AcmeCloud platform targeting enterprise migration. "
            "AcmeCorp prioritizes regulatory compliance and audit readiness."
        ),
        "evidence_pack": [
            {
                "artifact_id": "art_001",
                "summary": "AcmeCorp announced AcmeCloud platform launch with enterprise migration focus",
                "confidence": 0.85,
            },
            {
                "artifact_id": "art_002",
                "summary": "AcmeCorp regulatory compliance roadmap published targeting audit readiness",
                "confidence": 0.80,
            },
        ],
    }
    score, codes, refs, hint = evaluate_hop2_grounding(state, _hop2_rubric())
    assert score >= 0.70, f"expected STRONG, got {score}"
    assert any(r.startswith("artifact:") for r in refs)


def test_hop2_weak_when_brief_uncited():
    state = {
        "strategic_brief": (
            "Hello there hope this finds you well wanted to introduce widgets gadgets. "
            "Nothing here matches the evidence at all."
        ),
        "evidence_pack": [
            {
                "artifact_id": "art_001",
                "summary": "AcmeCorp regulatory compliance audit readiness enterprise",
                "confidence": 0.85,
            },
        ],
    }
    score, codes, refs, hint = evaluate_hop2_grounding(state, _hop2_rubric())
    assert score < 0.40
    assert "majority_claims_uncited" in codes


def test_hop2_raises_on_empty_evidence_pack():
    with pytest.raises(ValueError, match="evidence_pack"):
        evaluate_hop2_grounding(
            {"strategic_brief": "AcmeCorp launched.", "evidence_pack": []},
            _hop2_rubric(),
        )


def test_hop2_raises_on_no_claim_sentences():
    with pytest.raises(ValueError, match="claim-sentences"):
        evaluate_hop2_grounding(
            {
                "strategic_brief": "",
                "evidence_pack": [
                    {"artifact_id": "x", "summary": "x", "confidence": 0.9}
                ],
            },
            _hop2_rubric(),
        )


def test_hop2_judge_end_to_end_weak_routes_revise():
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop2_grounding.yaml",
        evaluate_fn=evaluate_hop2_grounding,
    )
    sc = judge.judge(
        {
            "strategic_brief": "Hello widgets gadgets unrelated. Nothing matters here.",
            "evidence_pack": [
                {
                    "artifact_id": "art_001",
                    "summary": "AcmeCorp regulatory compliance audit readiness",
                    "confidence": 0.85,
                }
            ],
        },
        emit_marker=False,
    )
    # judge_disposition_policy: weak_band_hop2_grounding -> REVISE / RETRY_HOP2
    assert sc.x3_disposition == "REVISE"


# ---------------------------------------------------------------------- #
# HOP8 narrative evaluator
# ---------------------------------------------------------------------- #


def _hop8_rubric() -> Rubric:
    return Rubric.load(RUBRIC_DIR / "judge_hop8_narrative.yaml")


def test_hop8_excellent_template_when_high_total_score():
    state = {
        "total_score": 0.93,
        "score_breakdown": {"alignment": 0.95, "tone": 0.92, "length": 0.90, "spam": 0.95},
    }
    score, codes, refs, hint = evaluate_hop8_narrative(state, _hop8_rubric())
    assert score == pytest.approx(0.93)
    assert "narrative_template:excellent" in codes
    narrative = next(r[len("narrative:"):] for r in refs if r.startswith("narrative:"))
    assert "0.93" in narrative
    assert hint == ""


def test_hop8_needs_work_template_when_low_total_score():
    state = {
        "total_score": 0.30,
        "score_breakdown": {"alignment": 0.10, "tone": 0.50, "length": 0.50, "spam": 0.40},
    }
    score, codes, refs, hint = evaluate_hop8_narrative(state, _hop8_rubric())
    assert score == pytest.approx(0.30)
    assert "narrative_template:needs_work" in codes
    assert "score_below_acceptable_floor" in codes
    narrative = next(r[len("narrative:"):] for r in refs if r.startswith("narrative:"))
    # Top gap (lowest-scoring dim) is alignment -> should appear in narrative.
    assert "alignment" in narrative.lower()


def test_hop8_acceptable_template_for_mid_score():
    state = {
        "total_score": 0.65,
        "score_breakdown": {"alignment": 0.70, "tone": 0.50, "length": 0.80, "spam": 0.60},
    }
    score, codes, refs, hint = evaluate_hop8_narrative(state, _hop8_rubric())
    assert "narrative_template:acceptable" in codes


def test_hop8_judge_end_to_end_strong_routes_allow():
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop8_narrative.yaml",
        evaluate_fn=evaluate_hop8_narrative,
    )
    sc = judge.judge(
        {
            "total_score": 0.92,
            "score_breakdown": {"alignment": 0.95, "tone": 0.90},
        },
        emit_marker=False,
    )
    assert sc.x3_disposition == "ALLOW"
    # Narrative ships in evidence_refs with "narrative:" prefix.
    assert any(r.startswith("narrative:") for r in sc.evidence_refs)


def test_hop8_judge_end_to_end_weak_routes_abstain():
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop8_narrative.yaml",
        evaluate_fn=evaluate_hop8_narrative,
    )
    sc = judge.judge(
        {
            "total_score": 0.20,
            "score_breakdown": {"alignment": 0.10, "spam": 0.30},
        },
        emit_marker=False,
    )
    # judge_disposition_policy: weak_band_hop8_narrative -> ABSTAIN
    assert sc.x3_disposition == "ABSTAIN"

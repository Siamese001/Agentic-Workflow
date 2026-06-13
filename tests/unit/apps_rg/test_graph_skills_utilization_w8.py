"""W8: graph skills utilization scorer + anti-gaming (D8)."""
from __future__ import annotations

import pytest

from apps_rg.runtime.graph_skills_utilization_scorer import (
    RECEIPT_SCHEMA,
    score_evidence_strength_for_skill_row,
    score_graph_skills_utilization,
    validate_scorer_inputs_neg6,
)
from apps_rg.runtime.validators.graph_skills_proof_common import GraphSkillsProofError


def _skill_row(
    skill_id: str,
    *,
    phrase: str,
    fact_id: str,
    forbidden: list[str] | None = None,
) -> dict:
    return {
        "skill_id": skill_id,
        "allowed_phrases": [phrase],
        "fact_id_links": [fact_id],
        "graph_hop_path": ["jd", "role", skill_id],
        "forbidden_phrases": forbidden or [],
    }


def test_utilization_passes_phrase_and_fact_grounding() -> None:
    row = _skill_row("sk_util", phrase="agentic ai platform", fact_id="fact_exec_001")
    text = "Built an agentic-ai platform for governed runtime delivery."
    coverage = {
        "sentences": [
            {"claim_text": text, "cited_fact_ids": ["fact_exec_001"]},
        ]
    }
    receipt = score_graph_skills_utilization(
        section_id="executive_summary",
        skill_rows=[row],
        resume_display_text=text,
        text_claim_coverage=coverage,
        allowed_fact_ids=["fact_exec_001"],
    )
    assert receipt["pass"] is True
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert "agentic ai platform" in receipt["used_phrases"]
    assert receipt["utilization_score"] == 1.0
    assert receipt["cited_fact_ids"] == ["fact_exec_001"]
    assert receipt["evidence_strength"]["schema"] == "apps_rg_evidence_strength_summary_v1"
    assert receipt["evidence_strength"]["eligible_skill_count"] == 1


def test_utilization_fails_phrase_only_without_fact() -> None:
    row = _skill_row("sk_phrase_only", phrase="platform engineering", fact_id="fact_comp_001")
    text = "Led platform-engineering initiatives across the estate."
    coverage = {"sentences": [{"claim_text": text, "cited_fact_ids": []}]}
    receipt = score_graph_skills_utilization(
        section_id="competencies",
        skill_rows=[row],
        resume_display_text=text,
        text_claim_coverage=coverage,
        allowed_fact_ids=["fact_comp_001"],
    )
    assert receipt["pass"] is False
    assert receipt["utilization_score"] == 0.0
    assert "sk_phrase_only" in receipt["unused_skill_ids"]


def test_utilization_detects_forbidden_phrase() -> None:
    row = _skill_row(
        "sk_bad",
        phrase="governed runtime",
        fact_id="fact_exec_002",
        forbidden=["unverified metric"],
    )
    text = "Delivered governed runtime with an unverified metric spike."
    coverage = {
        "sentences": [
            {"claim_text": text, "cited_fact_ids": ["fact_exec_002"]},
        ]
    }
    receipt = score_graph_skills_utilization(
        section_id="executive_summary",
        skill_rows=[row],
        resume_display_text=text,
        text_claim_coverage=coverage,
        allowed_fact_ids=["fact_exec_002"],
    )
    assert receipt["pass"] is False
    assert receipt["forbidden_phrase_violations"]


def test_utilization_excludes_suppressed_from_denominator() -> None:
    rows = [
        _skill_row("sk_a", phrase="insurtech", fact_id="fact_a"),
        _skill_row("sk_b", phrase="platform engineering", fact_id="fact_b"),
    ]
    text = "Scaled insurtech delivery with cited outcomes."
    coverage = {"sentences": [{"claim_text": text, "cited_fact_ids": ["fact_a"]}]}
    receipt = score_graph_skills_utilization(
        section_id="competencies",
        skill_rows=rows,
        resume_display_text=text,
        text_claim_coverage=coverage,
        allowed_fact_ids=["fact_a", "fact_b"],
        suppressed_skill_ids=[{"skill_id": "sk_b", "reason_code": "jd_mismatch"}],
    )
    assert receipt["eligible_skill_count"] == 1
    assert receipt["utilization_score"] == 1.0
    assert receipt["suppressed_skill_ids"] == [{"skill_id": "sk_b", "reason_code": "jd_mismatch"}]


def test_neg6_rejects_capsule_phrase_in_allowed_fact_ids() -> None:
    row = _skill_row("sk_neg6", phrase="capsule phrase token", fact_id="fact_x")
    with pytest.raises(GraphSkillsProofError, match="capsule phrase"):
        validate_scorer_inputs_neg6(
            section_id="executive_summary",
            skill_rows=[row],
            allowed_fact_ids=["capsule phrase token", "fact_x"],
        )


def test_semantic_variant_match_recorded() -> None:
    row = _skill_row("sk_var", phrase="agentic ai platform", fact_id="fact_var")
    text = "Operated an agentic-ai platform with measurable outcomes."
    coverage = {"sentences": [{"claim_text": text, "cited_fact_ids": ["fact_var"]}]}
    receipt = score_graph_skills_utilization(
        section_id="executive_summary",
        skill_rows=[row],
        resume_display_text=text,
        text_claim_coverage=coverage,
        allowed_fact_ids=["fact_var"],
    )
    assert receipt["pass"] is True
    assert "agentic ai platform" in receipt["used_phrases"]


def test_evidence_strength_scores_fact_metric_and_confidence_without_proof_promotion() -> None:
    row = {
        "skill_id": "skill_metric_backed",
        "confidence_grade": "HIGH",
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "fact_id_links": ["fact_a"],
        "linked_metric_outcome_ids": ["metric_a"],
        "external_claim_policy": "approved_metric_linked",
        "source_trace": ["archive/resume.md"],
    }
    scored = score_evidence_strength_for_skill_row(row)
    assert scored["evidence_strength_band"] == "HIGH"
    assert scored["evidence_strength_score"] >= 0.75
    assert scored["fact_id_count"] == 1
    assert scored["metric_outcome_id_count"] == 1
    assert scored["authority_note"] == "derived_score_only_not_claim_proof"


def test_evidence_strength_blocks_pending_or_unapproved_claims() -> None:
    row = {
        "skill_id": "skill_unapproved",
        "confidence_grade": "BLOCKED",
        "support_level": "USER_CONFIRMED_PENDING_SOURCE",
        "external_claim_policy": "not claimable without linked metric_outcome_id",
    }
    scored = score_evidence_strength_for_skill_row(row)
    assert scored["evidence_strength_band"] == "BLOCKED"
    assert scored["evidence_strength_score"] == 0.0
    assert "blocking_claim_policy" in scored["penalties"]

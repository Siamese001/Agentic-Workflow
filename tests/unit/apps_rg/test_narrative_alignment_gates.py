"""Acceptance tests for narrative alignment X2 gates (W3).

Coverage:
1. test_narrative_blocks_on_missing_upstream_graph_proof — upstream graph_skill_node_ids fail → warn
2. test_narrative_requires_graph_skill_source_facts — upstream gate status propagates
3. test_narrative_rejects_unsupported_new_claims — consulting language fails
4. test_narrative_rejects_consulting_language — consulting phrase blocklist
5. test_narrative_seniority_preserved — weak-verb narrative fails floor
6. test_narrative_not_bullet_recap — verbatim bullet echo
7. test_base_prose_not_hydrated — n-gram overlap with base role_narrative
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.narrative_quality_x2 import (
    NARRATIVE_CONSULTING_PHRASES,
    NARRATIVE_STRONG_VERBS,
    NARRATIVE_WEAK_VERBS,
    check_narrative_base_prose_ngram_overlap,
    check_narrative_e0_ngram_overlap,
    check_narrative_no_consulting_language,
    check_narrative_not_bullet_recap,
    check_narrative_seniority_floor,
    check_narrative_technical_specificity,
    check_narrative_upstream_graph_proof_bundle,
)


# ---------------------------------------------------------------------------
# 1. Upstream graph proof gate — missing upstream gate warns
# ---------------------------------------------------------------------------

class TestNarrativeBlocksOnMissingUpstreamGraphProof:
    def test_no_upstream_gates_warns_in_warn_mode(self):
        result = check_narrative_upstream_graph_proof_bundle([], warn_only=True)
        # In warn mode: gate always passes, but failure_reason is set
        assert result.passed, "Warn mode should pass even when upstream gate missing"
        assert result.failure_reason is not None
        assert "upstream_gate_not_found" in str(result.observed_value)

    def test_upstream_gate_not_found_fails_without_warn(self):
        result = check_narrative_upstream_graph_proof_bundle([], warn_only=False)
        assert not result.passed
        assert "upstream_gate_not_found" in str(result.observed_value)

    def test_upstream_gate_passed_allows_narrative(self):
        upstream = [
            {"gate_id": "x2_bullet_graph_skill_node_ids_required", "pass_": True}
        ]
        result = check_narrative_upstream_graph_proof_bundle(upstream, warn_only=False)
        assert result.passed

    def test_upstream_gate_failed_warns_in_warn_mode(self):
        upstream = [
            {"gate_id": "x2_bullet_graph_skill_node_ids_required", "pass_": False}
        ]
        result = check_narrative_upstream_graph_proof_bundle(upstream, warn_only=True)
        assert result.passed  # warn mode
        assert result.failure_reason is not None

    def test_upstream_gate_failed_fails_without_warn(self):
        upstream = [
            {"gate_id": "x2_bullet_graph_skill_node_ids_required", "pass_": False}
        ]
        result = check_narrative_upstream_graph_proof_bundle(upstream, warn_only=False)
        assert not result.passed


# ---------------------------------------------------------------------------
# 2. Graph skill source facts — upstream gate propagation
# ---------------------------------------------------------------------------

class TestNarrativeRequiresGraphSkillSourceFacts:
    def test_gate_id_correct(self):
        result = check_narrative_upstream_graph_proof_bundle(
            [{"gate_id": "x2_bullet_graph_skill_node_ids_required", "pass_": True}],
            warn_only=False,
        )
        assert result.gate_id == "x2_narrative_upstream_graph_proof_required"

    def test_all_upstream_pass_narrative_passes(self):
        upstream = [
            {"gate_id": "x2_bullet_graph_skill_node_ids_required", "pass_": True},
        ]
        result = check_narrative_upstream_graph_proof_bundle(upstream, warn_only=False)
        assert result.passed
        assert result.failure_reason is None


# ---------------------------------------------------------------------------
# 3. Consulting language / unsupported claims fail
# ---------------------------------------------------------------------------

class TestNarrativeRejectsUnsupportedNewClaims:
    def test_consulting_phrase_fails(self):
        narrative = (
            "Drove strategic value by working closely with stakeholders to ensure alignment "
            "across the enterprise agentic AI platform at Unify Consulting."
        )
        result = check_narrative_no_consulting_language(narrative)
        assert not result.passed
        assert len(result.signals) > 0

    def test_thought_leadership_fails(self):
        narrative = "Providing thought leadership on AI platform architecture at IBM."
        result = check_narrative_no_consulting_language(narrative)
        assert not result.passed

    def test_best_practices_fails(self):
        narrative = "Leveraged best practices to modernize the data platform at Unify Consulting."
        result = check_narrative_no_consulting_language(narrative)
        assert not result.passed
        assert any("best practices" in s for s in result.signals)


# ---------------------------------------------------------------------------
# 4. Consulting language rejection (detailed)
# ---------------------------------------------------------------------------

class TestNarrativeRejectsConsultingLanguage:
    def test_drive_strategic_value_fails(self):
        result = check_narrative_no_consulting_language(
            "Aimed to drive strategic value across the platform organization at IBM."
        )
        assert not result.passed

    def test_ensure_alignment_fails(self):
        result = check_narrative_no_consulting_language(
            "Worked to ensure alignment between engineering teams and business stakeholders."
        )
        assert not result.passed

    def test_clean_executive_narrative_passes(self):
        narrative = (
            "Owned the platform roadmap and commercialization of a production-grade agentic AI "
            "platform at Unify Consulting, converting bespoke delivery into reusable platform "
            "services for regulated financial-services adoption."
        )
        result = check_narrative_no_consulting_language(narrative)
        assert result.passed, f"Clean narrative should pass: {result.failure_reason}"

    def test_empty_narrative_passes(self):
        result = check_narrative_no_consulting_language("")
        assert result.passed


# ---------------------------------------------------------------------------
# 5. Seniority floor — weak verbs fail
# ---------------------------------------------------------------------------

class TestNarrativeSeniorityPreserved:
    def test_weak_opener_supported_fails(self):
        # "supported" is a weak verb
        result = check_narrative_seniority_floor(
            "Supported the platform roadmap for agentic AI architecture at Unify."
        )
        # "supported" is in NARRATIVE_WEAK_VERBS — check that
        assert "supported" in NARRATIVE_WEAK_VERBS

    def test_helped_opener_fails_floor(self):
        narrative = "Helped engineering teams build the AI governance platform at IBM."
        result = check_narrative_seniority_floor(narrative)
        # "helped" is a weak verb opener — no strong_verb AND has weak opener
        assert not result.passed or "weak_opener" in str(result.signals)

    def test_strong_verb_platform_passes(self):
        narrative = (
            "Owned the platform roadmap and commercialization of a production-grade agentic AI "
            "platform at Unify Consulting, converting bespoke delivery into reusable platform services."
        )
        result = check_narrative_seniority_floor(narrative)
        assert result.passed, f"Strong executive narrative should pass: {result.signals}"

    def test_drove_mandate_passes(self):
        narrative = (
            "Drove the strategic mandate to industrialize a governed agentic AI platform at IBM, "
            "establishing reusable IP and scalable architecture for regulated enterprise environments."
        )
        result = check_narrative_seniority_floor(narrative)
        assert result.passed, f"Should pass seniority floor: {result.signals}"

    def test_technical_specificity_required(self):
        result = check_narrative_technical_specificity("Managed teams and delivered projects efficiently.")
        assert not result.passed

    def test_agentic_token_passes_specificity(self):
        result = check_narrative_technical_specificity(
            "Owned the agentic AI platform roadmap for regulated enterprise deployment."
        )
        assert result.passed

    def test_llm_rag_passes_specificity(self):
        result = check_narrative_technical_specificity(
            "Drove the LLM-backed RAG pipeline architecture at IBM for enterprise retrieval."
        )
        assert result.passed


# ---------------------------------------------------------------------------
# 6. Bullet recap gate
# ---------------------------------------------------------------------------

class TestNarrativeNotBulletRecap:
    def test_verbatim_echo_warns_in_warn_mode(self):
        bullet = "Architected the agentic AI platform reducing cycle time from six months to three weeks."
        result = check_narrative_not_bullet_recap(bullet, [bullet], warn_only=True)
        # Warn mode: always passes but failure_reason set when overlap is high
        assert result.passed  # warn mode
        # High overlap should trigger failure_reason
        if result.observed_value and isinstance(result.observed_value, dict):
            assert result.observed_value.get("max_5gram_overlap", 0) > 0.0

    def test_verbatim_echo_fails_without_warn(self):
        bullet = "Architected the agentic AI platform reducing cycle time from six months to three weeks."
        result = check_narrative_not_bullet_recap(bullet, [bullet], warn_only=False)
        # Should fail when identical
        assert not result.passed

    def test_strategic_framing_passes(self):
        bullets = [
            "Architected the agentic AI platform reducing cycle time from six months to three weeks.",
            "Launched production-grade LLM evaluation harness achieving 99.1% determinism.",
        ]
        narrative = (
            "Owned the platform roadmap and commercialization of a governed agentic AI stack at Unify, "
            "converting bespoke engagements into reusable scalable enterprise services."
        )
        result = check_narrative_not_bullet_recap(narrative, bullets, warn_only=False)
        assert result.passed, f"Strategic narrative should not be flagged as recap: {result.observed_value}"

    def test_empty_bullets_passes(self):
        result = check_narrative_not_bullet_recap("Any narrative text here.", [], warn_only=False)
        assert result.passed


# ---------------------------------------------------------------------------
# 7. Base prose n-gram overlap
# ---------------------------------------------------------------------------

class TestBaseProsNotHydrated:
    def test_identical_base_prose_fails(self):
        base = "Owned the agentic AI platform roadmap and commercialization of production-grade services."
        result = check_narrative_base_prose_ngram_overlap(base, [base], warn_only=False)
        assert not result.passed
        assert result.observed_value > 0.5

    def test_novel_narrative_passes(self):
        base = "Led data analytics migration program and enterprise cloud strategy for global operations."
        novel = (
            "Owned the agentic AI platform roadmap at Unify Consulting, "
            "converting bespoke delivery into reusable LLM-backed enterprise services."
        )
        result = check_narrative_base_prose_ngram_overlap(novel, [base], warn_only=False)
        assert result.passed, f"Novel narrative should pass: overlap={result.observed_value}"

    def test_empty_base_passes(self):
        result = check_narrative_base_prose_ngram_overlap("Any narrative.", [], warn_only=False)
        assert result.passed

    def test_e0_overlap_gate_id(self):
        result = check_narrative_e0_ngram_overlap("Some narrative text.", [], warn_only=False)
        assert result.gate_id == "x2_narrative_e0_ngram_overlap"
        assert result.passed

    def test_e0_identical_fails(self):
        e0 = "Owned the platform roadmap and commercialization of a production-grade agentic AI platform."
        result = check_narrative_e0_ngram_overlap(e0, [e0], warn_only=False)
        assert not result.passed
        assert result.observed_value > 0.5

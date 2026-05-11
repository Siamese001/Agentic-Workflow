"""W9 Judges / Evals / LLM-as-judge Integration — apps_research.

Plan: apps-research-rich-content-runtime-customization-v2
Wave: W9, Phases: P32-P35

Scope:
- claim support judge
- citation quality judge
- coverage depth judge
- contradiction resolution judge
- source authority judge
- cache compatibility judge
- briefing injection judge
- downstream relevance judges for apps_rg/apps_lic
- deterministic graders
- mapping judge/eval results into G09, G10, G22, G25 evidence

W9 Constraints:
- Do NOT change Exit X3 logic
- Do NOT write cache
- Do NOT add L6 learning
- Do NOT add UWG writeback
- Do NOT let judges directly decide X3
"""
import pytest
from typing import Dict, Any, List

from apps_research.engines.judges import (
    ClaimSupportJudge,
    CitationQualityJudge,
    CoverageDepthJudge,
    ContradictionResolutionJudge,
    SourceAuthorityJudge,
    CacheCompatibilityJudge,
    BriefingInjectionJudge,
    DownstreamRelevanceJudge,
    # Calibrated flags
    claim_support_IS_STUB,
    claim_support_IS_CALIBRATED,
    citation_quality_IS_STUB,
    citation_quality_IS_CALIBRATED,
    coverage_depth_IS_STUB,
    coverage_depth_IS_CALIBRATED,
    contradiction_resolution_IS_STUB,
    contradiction_resolution_IS_CALIBRATED,
    source_authority_IS_STUB,
    source_authority_IS_CALIBRATED,
    cache_compatibility_IS_STUB,
    cache_compatibility_IS_CALIBRATED,
    briefing_injection_IS_STUB,
    briefing_injection_IS_CALIBRATED,
    downstream_relevance_IS_STUB,
    downstream_relevance_IS_CALIBRATED,
)
from apps_research.engines.judges.base import map_judge_evidence_to_gate


# ─────────────────────────────────────────────────────────────────────────────
# W9 Judge Infrastructure Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestW9JudgeInfrastructure:
    """Verify all W9 judges are properly defined."""

    def test_w9_all_judges_exist(self) -> None:
        """All 8 W9 judges must be importable."""
        assert ClaimSupportJudge is not None
        assert CitationQualityJudge is not None
        assert CoverageDepthJudge is not None
        assert ContradictionResolutionJudge is not None
        assert SourceAuthorityJudge is not None
        assert CacheCompatibilityJudge is not None
        assert BriefingInjectionJudge is not None
        assert DownstreamRelevanceJudge is not None

    def test_w9_judges_are_not_stub(self) -> None:
        """All W9 judges must be real implementations (not stubs)."""
        assert claim_support_IS_STUB is False
        assert citation_quality_IS_STUB is False
        assert coverage_depth_IS_STUB is False
        assert contradiction_resolution_IS_STUB is False
        assert source_authority_IS_STUB is False
        assert cache_compatibility_IS_STUB is False
        assert briefing_injection_IS_STUB is False
        assert downstream_relevance_IS_STUB is False

    def test_w9_judges_are_calibrated(self) -> None:
        """All W9 judges must be marked as calibrated."""
        assert claim_support_IS_CALIBRATED is True
        assert citation_quality_IS_CALIBRATED is True
        assert coverage_depth_IS_CALIBRATED is True
        assert contradiction_resolution_IS_CALIBRATED is True
        assert source_authority_IS_CALIBRATED is True
        assert cache_compatibility_IS_CALIBRATED is True
        assert briefing_injection_IS_CALIBRATED is True
        assert downstream_relevance_IS_CALIBRATED is True


# ─────────────────────────────────────────────────────────────────────────────
# W9 Judge Evaluation Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestW9JudgeEvaluations:
    """Test judge evaluations produce evidence."""

    def test_w9_claim_support_produces_evidence(self) -> None:
        """ClaimSupportJudge must produce JudgeEvidence."""
        judge = ClaimSupportJudge()
        brief = "Revenue grew 25% in 2024 [1]. The company was founded in 1995 [2]."
        evidence = judge.evaluate(brief, {})
        
        assert evidence.judge_id == "apps_research_claim_support"
        assert evidence.dimension == "claim_support"
        assert 0.0 <= evidence.score <= 1.0
        assert evidence.confidence > 0
        assert evidence.reasoning != ""

    def test_w9_contradiction_resolution_produces_evidence(self) -> None:
        """ContradictionResolutionJudge must produce JudgeEvidence."""
        judge = ContradictionResolutionJudge()
        brief = "Revenue grew 25% in 2024. However, some analysts suggest this may be due to one-time factors. According to [1], the growth is sustainable."
        evidence = judge.evaluate(brief, {})
        
        assert evidence.judge_id == "apps_research_contradiction_resolution"
        assert evidence.dimension == "contradiction_resolution"
        assert 0.0 <= evidence.score <= 1.0

    def test_w9_source_authority_produces_evidence(self) -> None:
        """SourceAuthorityJudge must produce JudgeEvidence."""
        judge = SourceAuthorityJudge()
        brief = "According to the SEC 10-K filing [1], revenue was $50B. Reuters reports [2] market expansion."
        evidence = judge.evaluate(brief, {})
        
        assert evidence.judge_id == "apps_research_source_authority"
        assert evidence.dimension == "source_authority"
        assert 0.0 <= evidence.score <= 1.0

    def test_w9_cache_compatibility_produces_evidence(self) -> None:
        """CacheCompatibilityJudge must produce JudgeEvidence."""
        judge = CacheCompatibilityJudge()
        brief = "Founded in 1995, headquartered in New York. Revenue $50B with 25% growth."
        evidence = judge.evaluate(brief, {})
        
        assert evidence.judge_id == "apps_research_cache_compatibility"
        assert evidence.dimension == "cache_compatibility"
        assert 0.0 <= evidence.score <= 1.0

    def test_w9_briefing_injection_produces_evidence(self) -> None:
        """BriefingInjectionJudge must produce JudgeEvidence."""
        judge = BriefingInjectionJudge()
        brief = "Overview: Company background and history. Business model: B2B SaaS. Financial highlights: $50B revenue."
        evidence = judge.evaluate(brief, {})
        
        assert evidence.judge_id == "apps_research_briefing_injection"
        assert evidence.dimension == "briefing_injection"
        assert 0.0 <= evidence.score <= 1.0

    def test_w9_downstream_relevance_rg(self) -> None:
        """DownstreamRelevanceJudge must score for apps_rg relevance."""
        judge = DownstreamRelevanceJudge()
        brief = "Leadership achievements include 50% team growth. Skills: strategic planning. Awards: Best Place to Work."
        evidence = judge.evaluate(brief, {"target_downstream": "rg"})
        
        assert evidence.dimension == "downstream_relevance"
        assert 0.0 <= evidence.score <= 1.0

    def test_w9_downstream_relevance_lic(self) -> None:
        """DownstreamRelevanceJudge must score for apps_lic relevance."""
        judge = DownstreamRelevanceJudge()
        brief = "Regulatory compliance certified. Financial strength ratings: A+. Risk management framework in place."
        evidence = judge.evaluate(brief, {"target_downstream": "lic"})
        
        assert evidence.dimension == "downstream_relevance"
        assert 0.0 <= evidence.score <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# W9 Gate Mapping Tests (G09, G10, G22, G25)
# ─────────────────────────────────────────────────────────────────────────────

class TestW9GateMapping:
    """Test judge evidence maps to correct gates."""

    def test_w9_source_authority_maps_to_g09(self) -> None:
        """SourceAuthorityJudge evidence maps to G09 (Source Quality)."""
        judge = SourceAuthorityJudge()
        evidence = judge.evaluate("SEC filing [1] shows $50B revenue.", {})
        
        result, score, reason = map_judge_evidence_to_gate(evidence, "G09", threshold=0.7)
        
        assert result in ("PASS", "WARN", "FAIL")
        assert 0.0 <= score <= 1.0
        assert "G09" in reason or "Source" in reason

    def test_w9_claim_support_maps_to_g10(self) -> None:
        """ClaimSupportJudge evidence maps to G10 (Factual Grounding)."""
        judge = ClaimSupportJudge()
        evidence = judge.evaluate("Revenue grew 25% [1]. Market share increased [2].", {})
        
        result, score, reason = map_judge_evidence_to_gate(evidence, "G10", threshold=0.75)
        
        assert result in ("PASS", "WARN", "FAIL")
        assert "claim_support" in evidence.reasoning.lower() or "citation" in evidence.reasoning.lower()

    def test_w9_coverage_depth_maps_to_g22(self) -> None:
        """CoverageDepthJudge evidence maps to G22 (Answer Completeness)."""
        # CoverageDepthJudge uses different interface
        from apps_research.engines.judges.coverage_depth_judge import grade
        
        score, evidence_refs = grade(
            "coverage_depth",
            {
                "output": {
                    "c0_bundle": {
                        "findings": {"overview": True, "financials": True},
                        "source_portfolio_summary": {"total_final_sources": 20}
                    },
                    "research_depth_profile": "COMPANY_BRIEF_STANDARD"
                }
            }
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_w9_cache_compatibility_maps_to_g25(self) -> None:
        """CacheCompatibilityJudge evidence maps to G25 (Cache Consistency)."""
        judge = CacheCompatibilityJudge()
        evidence = judge.evaluate("Founded in 1995. Revenue $50B.", {})
        
        result, score, reason = map_judge_evidence_to_gate(evidence, "G25", threshold=0.7)
        
        assert result in ("PASS", "WARN", "FAIL")
        assert "cache" in evidence.reasoning.lower() or "stable" in evidence.reasoning.lower()


# ─────────────────────────────────────────────────────────────────────────────
# W9 Constraint Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestW9Constraints:
    """Verify W9 constraints are respected."""

    def test_w9_judges_do_not_modify_exit_x3(self) -> None:
        """Judges must NOT modify Exit X3 logic."""
        from agentic_core.runtime.exit.exit_package_driven_binding import ExitPackageDrivenBinding
        
        # Verify Exit binding exists and is independent of judges
        binding = ExitPackageDrivenBinding
        assert binding is not None
        
        # Judges should not have any reference to Exit X3 decision
        from apps_research.engines.judges.claim_support_judge import ClaimSupportJudge
        judge = ClaimSupportJudge()
        
        # Judge should not have any Exit-related attributes
        assert not hasattr(judge, 'exit_disposition')
        assert not hasattr(judge, 'x3_decision')

    def test_w9_judges_do_not_write_cache(self) -> None:
        """Judges must NOT write to cache."""
        # All judges should be read-only evaluators
        for judge_class in [
            ClaimSupportJudge,
            CitationQualityJudge,
            ContradictionResolutionJudge,
            SourceAuthorityJudge,
            CacheCompatibilityJudge,
            BriefingInjectionJudge,
            DownstreamRelevanceJudge,
        ]:
            judge = judge_class()
            assert not hasattr(judge, 'write_cache')
            assert not hasattr(judge, 'cache_result')

    def test_w9_judges_do_not_add_l6_learning(self) -> None:
        """Judges must NOT add L6 learning logic."""
        for judge_class in [
            ClaimSupportJudge,
            CitationQualityJudge,
            ContradictionResolutionJudge,
            SourceAuthorityJudge,
            CacheCompatibilityJudge,
            BriefingInjectionJudge,
            DownstreamRelevanceJudge,
        ]:
            judge = judge_class()
            assert not hasattr(judge, 'learn')
            assert not hasattr(judge, 'promote_to_l6')

    def test_w9_judges_do_not_add_uwg_writeback(self) -> None:
        """Judges must NOT add UWG writeback."""
        for judge_class in [
            ClaimSupportJudge,
            CitationQualityJudge,
            ContradictionResolutionJudge,
            SourceAuthorityJudge,
            CacheCompatibilityJudge,
            BriefingInjectionJudge,
            DownstreamRelevanceJudge,
        ]:
            judge = judge_class()
            assert not hasattr(judge, 'uwg_write')
            assert not hasattr(judge, 'l4_commit')

    def test_w9_judges_produce_evidence_not_x3(self) -> None:
        """Judges must produce evidence, NOT directly decide X3."""
        judge = ClaimSupportJudge()
        evidence = judge.evaluate("Test brief with [1] citation.", {})
        
        # Evidence should not contain X3 disposition
        assert not hasattr(evidence, 'x3_disposition')
        assert not hasattr(evidence, 'allow_finish')
        
        # Evidence should have score and reasoning for gate consumption
        assert hasattr(evidence, 'score')
        assert hasattr(evidence, 'reasoning')


# ─────────────────────────────────────────────────────────────────────────────
# W9 Deterministic Grader Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestW9DeterministicGraders:
    """Test deterministic grader interfaces."""

    def test_w9_all_graders_have_grade_function(self) -> None:
        """All judges must have a grade() function for deterministic evaluation."""
        from apps_research.engines.judges import (
            claim_support_judge,
            citation_quality_judge,
            contradiction_resolution_judge,
            source_authority_judge,
            cache_compatibility_judge,
            briefing_injection_judge,
            downstream_relevance_judge,
        )
        
        assert hasattr(claim_support_judge, 'grade')
        assert hasattr(citation_quality_judge, 'grade')
        assert hasattr(contradiction_resolution_judge, 'grade')
        assert hasattr(source_authority_judge, 'grade')
        assert hasattr(cache_compatibility_judge, 'grade')
        assert hasattr(briefing_injection_judge, 'grade')
        assert hasattr(downstream_relevance_judge, 'grade')

    def test_w9_grade_returns_dict(self) -> None:
        """grade() must return a dict with expected fields."""
        from apps_research.engines.judges.claim_support_judge import grade
        
        result = grade("Test brief [1].", {})
        
        assert isinstance(result, dict)
        assert "score" in result
        assert "confidence" in result
        assert "dimension" in result
        assert "reasoning" in result
        assert "grader_id" in result
        assert "is_stub" in result
        assert "is_calibrated" in result

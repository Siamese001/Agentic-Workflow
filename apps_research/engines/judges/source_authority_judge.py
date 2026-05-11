"""Source Authority Judge — W9

Evaluates the authority/trustworthiness of sources cited in the brief.
Maps to G09 (Source Quality & Attribution).
"""
from typing import Any, Dict, List, Tuple
import re

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class SourceAuthorityJudge(BaseResearchJudge):
    """Deterministic grader for source authority assessment."""
    
    judge_id: str = "apps_research_source_authority"
    dimension: str = "source_authority"
    version: str = "W9.0.0"
    
    # Source tier indicators
    TIER_1_INDICATORS = [
        "sec.gov", "10-k", "10-q", "annual report", "sec filing",
        "earnings call", "press release", "official"
    ]
    TIER_2_INDICATORS = [
        "reuters", "bloomberg", "wsj", "wall street journal",
        "financial times", "cnbc", "forbes", "fortune"
    ]
    TIER_3_INDICATORS = [
        "wikipedia", "blog", "medium", "linkedin", "twitter"
    ]
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate source authority.
        
        Heuristic based on citation quality indicators:
        - Tier 1 (primary): SEC filings, official reports
        - Tier 2 (credible): Major financial news
        - Tier 3 (supplemental): Other sources
        """
        brief_lower = brief.lower()
        
        # Count sources by tier
        tier_1_count = sum(brief_lower.count(indicator) for indicator in self.TIER_1_INDICATORS)
        tier_2_count = sum(brief_lower.count(indicator) for indicator in self.TIER_2_INDICATORS)
        tier_3_count = sum(brief_lower.count(indicator) for indicator in self.TIER_3_INDICATORS)
        
        total_refs = tier_1_count + tier_2_count + tier_3_count
        
        if total_refs == 0:
            # No identifiable sources
            score = 0.5  # Neutral - cannot assess
            confidence = 0.4
            reasoning = "No identifiable authority indicators in citations"
        else:
            # Weighted score: Tier 1 = 1.0, Tier 2 = 0.8, Tier 3 = 0.5
            weighted_score = (
                (tier_1_count * 1.0) +
                (tier_2_count * 0.8) +
                (tier_3_count * 0.5)
            ) / total_refs
            
            # Bonus for diversity (having multiple tiers)
            diversity_bonus = 0.0
            tiers_present = sum([
                tier_1_count > 0,
                tier_2_count > 0,
                tier_3_count > 0
            ])
            if tiers_present >= 2:
                diversity_bonus = 0.05
            
            score = min(1.0, weighted_score + diversity_bonus)
            confidence = 0.75 if tier_1_count > 0 else 0.60
            
            reasoning = (
                f"Sources: {tier_1_count} primary, {tier_2_count} credible, "
                f"{tier_3_count} supplemental (diversity_bonus={diversity_bonus:.2f})"
            )
        
        return JudgeEvidence(
            judge_id=self.judge_id,
            dimension=self.dimension,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            evidence_refs=(f"judge://{self.judge_id}/evaluation",),
        )


# Deterministic grader interface
IS_STUB = False
IS_CALIBRATED = True
GRADER_ID = "apps_research_source_authority"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = SourceAuthorityJudge()
    evidence = judge.evaluate(brief, context)
    
    return {
        "score": evidence.score,
        "confidence": evidence.confidence,
        "dimension": evidence.dimension,
        "reasoning": evidence.reasoning,
        "grader_id": GRADER_ID,
        "is_stub": IS_STUB,
        "is_calibrated": IS_CALIBRATED,
    }

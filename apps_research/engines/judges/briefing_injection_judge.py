"""Briefing Injection Judge — W9

Evaluates whether the brief properly injects source briefing context.
Maps to G22 (Answer Completeness).
"""
from typing import Any, Dict
import re

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class BriefingInjectionJudge(BaseResearchJudge):
    """Deterministic grader for briefing injection assessment."""
    
    judge_id: str = "apps_research_briefing_injection"
    dimension: str = "briefing_injection"
    version: str = "W9.0.0"
    
    # Indicators of proper briefing coverage
    INJECTION_INDICATORS = [
        "overview", "summary", "introduction", "background",
        "history", "founded", "headquarters", "leadership",
        "revenue", "employees", "market", "industry"
    ]
    
    # Company section indicators
    SECTION_INDICATORS = [
        "business model", "competitive landscape", "financial highlights",
        "recent developments", "strategic initiatives", "risk factors"
    ]
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate briefing injection.
        
        Heuristic:
        - Count injection indicators (overview, background, etc.)
        - Count section coverage
        - Score based on comprehensive coverage
        """
        brief_lower = brief.lower()
        
        # Count injection indicators
        injection_count = sum(
            1 for indicator in self.INJECTION_INDICATORS
            if indicator in brief_lower
        )
        
        # Count section indicators
        section_count = sum(
            1 for indicator in self.SECTION_INDICATORS
            if indicator in brief_lower
        )
        
        # Calculate coverage
        total_possible = len(self.INJECTION_INDICATORS) + len(self.SECTION_INDICATORS)
        coverage = (injection_count + section_count) / total_possible
        
        # Score based on coverage
        if coverage >= 0.7:
            score = 0.85 + (coverage - 0.7) * 0.5
        elif coverage >= 0.4:
            score = 0.60 + (coverage - 0.4) * 0.83
        else:
            score = 0.30 + coverage * 0.75
        
        score = min(1.0, max(0.0, score))
        
        # Confidence based on coverage completeness
        confidence = 0.80 if coverage >= 0.6 else 0.65
        
        reasoning = (
            f"Injection coverage: {injection_count}/{len(self.INJECTION_INDICATORS)} "
            f"general, {section_count}/{len(self.SECTION_INDICATORS)} sections "
            f"(coverage={coverage:.2f})"
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
GRADER_ID = "apps_research_briefing_injection"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = BriefingInjectionJudge()
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

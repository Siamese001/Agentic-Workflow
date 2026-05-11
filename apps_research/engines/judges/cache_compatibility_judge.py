"""Cache Compatibility Judge — W9

Evaluates whether brief content is compatible with semantic cache expectations.
Maps to G25 (Cache Consistency & Relevance).

NOTE: Does NOT write to cache (W9 constraint).
Only evaluates compatibility for potential future caching.
"""
from typing import Any, Dict
import re

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class CacheCompatibilityJudge(BaseResearchJudge):
    """Deterministic grader for cache compatibility assessment."""
    
    judge_id: str = "apps_research_cache_compatibility"
    dimension: str = "cache_compatibility"
    version: str = "W9.0.0"
    
    # Factors that make content cacheable/stable
    STABLE_INDICATORS = [
        r"\d{4}",  # Years (time-stable facts)
        r"\$[\d,]+\s*(million|billion|m|b)?",  # Financial figures
        r"\d+\.\d+%",  # Percentages
        r"founded in \d{4}",  # Founding dates
        r"headquartered in",  # Location facts
        r"ceo", "chief executive", "president", "founder",  # People
    ]
    
    # Factors that make content volatile (not cacheable)
    VOLATILE_INDICATORS = [
        "today", "yesterday", "last week", "this month",
        "breaking", "just announced", "recently", "upcoming"
    ]
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate cache compatibility.
        
        Heuristic:
        - Stable facts (dates, figures, locations) = high cacheability
        - Volatile references (today, breaking, upcoming) = low cacheability
        """
        brief_lower = brief.lower()
        
        # Count stable indicators
        stable_count = 0
        for pattern in self.STABLE_INDICATORS:
            stable_count += len(re.findall(pattern, brief, re.IGNORECASE))
        
        # Count volatile indicators
        volatile_count = 0
        for indicator in self.VOLATILE_INDICATORS:
            volatile_count += brief_lower.count(indicator)
        
        # Calculate stability ratio
        total_indicators = stable_count + volatile_count
        
        if total_indicators == 0:
            # No clear indicators - moderate cacheability
            score = 0.60
            confidence = 0.50
            reasoning = "No clear cacheability indicators in brief"
        else:
            stability_ratio = stable_count / total_indicators
            
            # Score based on stability ratio
            if stability_ratio >= 0.8:
                score = 0.90 + (stability_ratio - 0.8) * 0.5
            elif stability_ratio >= 0.5:
                score = 0.70 + (stability_ratio - 0.5) * 0.67
            else:
                score = 0.40 + stability_ratio * 0.60
            
            score = min(1.0, max(0.0, score))
            confidence = 0.75 if stable_count > volatile_count else 0.60
            
            reasoning = (
                f"Stable indicators: {stable_count}, Volatile: {volatile_count} "
                f"(stability_ratio={stability_ratio:.2f})"
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
GRADER_ID = "apps_research_cache_compatibility"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = CacheCompatibilityJudge()
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

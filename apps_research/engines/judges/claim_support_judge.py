"""Claim Support Judge — W9

Evaluates whether claims in the brief are supported by evidence.
Maps to G10 (Factual Grounding).
"""
from typing import Any, Dict, List, Tuple
import re

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class ClaimSupportJudge(BaseResearchJudge):
    """Deterministic grader for claim-to-evidence support."""
    
    judge_id: str = "apps_research_claim_support"
    dimension: str = "claim_support"
    version: str = "W9.0.0"
    
    # Thresholds for claim support
    SUPPORTED_THRESHOLD = 0.75
    PARTIAL_THRESHOLD = 0.50
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate claim support in brief.
        
        Deterministic heuristic:
        1. Extract claims (sentences with factual assertions)
        2. Check for citation markers [1], [2], etc.
        3. Score based on citation coverage
        """
        # Extract claims (sentences ending in period with numbers, dates, or specific facts)
        claim_pattern = r'[^.]+?(?:\d{4}|\$[\d,]+|percent|percentage|%)[^.]*\.'
        claims = re.findall(claim_pattern, brief, re.IGNORECASE)
        
        # Count claims with citations
        claims_with_citations = 0
        for claim in claims:
            if re.search(r'\[\d+\]', claim):
                claims_with_citations += 1
        
        total_claims = len(claims) if claims else 1  # Avoid div by zero
        support_ratio = claims_with_citations / total_claims
        
        # Score based on support ratio
        if support_ratio >= 0.8:
            score = 0.85 + (support_ratio - 0.8) * 0.375  # 0.85-1.0
        elif support_ratio >= 0.5:
            score = 0.60 + (support_ratio - 0.5) * 0.833  # 0.60-0.85
        else:
            score = support_ratio * 1.2  # 0-0.60
        
        score = min(1.0, max(0.0, score))
        
        reasoning = (
            f"Found {len(claims)} claims, {claims_with_citations} with citations "
            f"(support_ratio={support_ratio:.2f})"
        )
        
        return JudgeEvidence(
            judge_id=self.judge_id,
            dimension=self.dimension,
            score=score,
            confidence=0.75 if claims else 0.5,  # Lower confidence if no claims found
            reasoning=reasoning,
            evidence_refs=(f"judge://{self.judge_id}/evaluation",),
        )


# Deterministic grader interface
IS_STUB = False
IS_CALIBRATED = True
GRADER_ID = "apps_research_claim_support"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = ClaimSupportJudge()
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

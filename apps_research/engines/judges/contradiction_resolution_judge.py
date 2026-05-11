"""Contradiction Resolution Judge — W9

Evaluates whether contradictions in sources are resolved in the brief.
Maps to G10 (Factual Grounding).
"""
from typing import Any, Dict, List, Set

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class ContradictionResolutionJudge(BaseResearchJudge):
    """Deterministic grader for contradiction detection and resolution."""
    
    judge_id: str = "apps_research_contradiction_resolution"
    dimension: str = "contradiction_resolution"
    version: str = "W9.0.0"
    
    # Contradiction indicators
    CONTRADICTION_MARKERS = [
        "however", "but", "although", "whereas", "conversely",
        "on the other hand", "in contrast", "despite", "nevertheless"
    ]
    
    RESOLUTION_MARKERS = [
        "according to", "based on", "as stated in", "per",
        "[1]", "[2]", "[3]", "sources indicate"
    ]
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate contradiction resolution.
        
        Heuristic:
        1. Count contradiction markers (potential conflicts)
        2. Count resolution markers (citations that resolve)
        3. Score based on resolution coverage
        """
        brief_lower = brief.lower()
        
        # Count contradiction markers
        contradiction_count = sum(
            brief_lower.count(marker)
            for marker in self.CONTRADICTION_MARKERS
        )
        
        # Count resolution markers (citations)
        resolution_count = sum(
            brief_lower.count(marker)
            for marker in self.RESOLUTION_MARKERS
        )
        
        # Score logic
        if contradiction_count == 0:
            # No contradictions detected = perfect score
            score = 1.0
            confidence = 0.7  # Moderate confidence - might have missed contradictions
            reasoning = "No contradiction markers detected in brief"
        else:
            # Calculate resolution ratio
            resolution_ratio = resolution_count / (contradiction_count * 2)
            
            if resolution_ratio >= 0.8:
                score = 0.90 + (resolution_ratio - 0.8) * 0.5
            elif resolution_ratio >= 0.5:
                score = 0.70 + (resolution_ratio - 0.5) * 0.67
            else:
                score = 0.40 + resolution_ratio * 0.60
            
            score = min(1.0, max(0.0, score))
            confidence = 0.80 if resolution_count > 0 else 0.60
            
            reasoning = (
                f"Detected {contradiction_count} potential contradictions, "
                f"{resolution_count} resolution markers (ratio={resolution_ratio:.2f})"
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
GRADER_ID = "apps_research_contradiction_resolution"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = ContradictionResolutionJudge()
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

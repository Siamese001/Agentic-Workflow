"""Downstream Relevance Judge — W9

Evaluates whether brief content is relevant for downstream apps (apps_rg, apps_lic).
Maps to G25 (Cache Consistency & Relevance).

NOTE: This is an evaluation-only judge — does NOT write cache or modify downstream.
"""
from typing import Any, Dict
import re

from apps_research.engines.judges.base import BaseResearchJudge, JudgeEvidence


class DownstreamRelevanceJudge(BaseResearchJudge):
    """Deterministic grader for downstream relevance assessment."""
    
    judge_id: str = "apps_research_downstream_relevance"
    dimension: str = "downstream_relevance"
    version: str = "W9.0.0"
    
    # Relevance for apps_rg (resume generation)
    RG_RELEVANT_INDICATORS = [
        "skills", "experience", "leadership", "achievements",
        "revenue growth", "market expansion", "innovation",
        "team size", "global presence", "awards"
    ]
    
    # Relevance for apps_lic (insurance licensing)
    LIC_RELEVANT_INDICATORS = [
        "regulatory", "compliance", "license", "certification",
        "financial strength", "ratings", "capital", "risk management",
        "governance", "audit", "filing"
    ]
    
    def evaluate(self, brief: str, context: Dict[str, Any]) -> JudgeEvidence:
        """Evaluate downstream relevance.
        
        Heuristic:
        - Count relevance indicators for each downstream app
        - Score based on coverage for intended downstream
        """
        brief_lower = brief.lower()
        target_downstream = context.get("target_downstream", "both")  # rg, lic, or both
        
        # Count relevance indicators
        rg_count = sum(
            1 for indicator in self.RG_RELEVANT_INDICATORS
            if indicator in brief_lower
        )
        
        lic_count = sum(
            1 for indicator in self.LIC_RELEVANT_INDICATORS
            if indicator in brief_lower
        )
        
        # Calculate relevance score based on target
        if target_downstream == "rg":
            max_possible = len(self.RG_RELEVANT_INDICATORS)
            coverage = rg_count / max_possible if max_possible > 0 else 0
            score = min(1.0, 0.50 + coverage * 0.5)
            reasoning = f"Resume-gen relevance: {rg_count}/{len(self.RG_RELEVANT_INDICATORS)} indicators"
            
        elif target_downstream == "lic":
            max_possible = len(self.LIC_RELEVANT_INDICATORS)
            coverage = lic_count / max_possible if max_possible > 0 else 0
            score = min(1.0, 0.50 + coverage * 0.5)
            reasoning = f"Licensing relevance: {lic_count}/{len(self.LIC_RELEVANT_INDICATORS)} indicators"
            
        else:  # both
            rg_coverage = rg_count / len(self.RG_RELEVANT_INDICATORS)
            lic_coverage = lic_count / len(self.LIC_RELEVANT_INDICATORS)
            coverage = (rg_coverage + lic_coverage) / 2
            score = min(1.0, 0.40 + coverage * 0.6)
            reasoning = (
                f"Multi-downstream: RG={rg_count}, LIC={lic_count} "
                f"(avg_coverage={coverage:.2f})"
            )
        
        confidence = 0.75 if coverage >= 0.5 else 0.60
        
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
GRADER_ID = "apps_research_downstream_relevance"


def grade(brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for deterministic grading."""
    judge = DownstreamRelevanceJudge()
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

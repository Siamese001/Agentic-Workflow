"""Base judge infrastructure for apps_research W9 judges.

W9 Scope:
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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from agentic_core.runtime.contracts.judge_types import JudgeResult


@dataclass(frozen=True, slots=True)
class JudgeEvidence:
    """Evidence produced by a judge evaluation."""
    judge_id: str
    dimension: str
    score: float
    confidence: float
    reasoning: str
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_gate_evidence(self, gate_id: str) -> Dict[str, Any]:
        """Convert judge evidence to gate evidence format."""
        return {
            "gate_id": gate_id,
            "dimension": self.dimension,
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_refs": list(self.evidence_refs),
            "judge_id": self.judge_id,
            "timestamp": self.timestamp,
        }


class BaseResearchJudge:
    """W9 stub base for apps_research judges.
    
    Judges are stubs only — execution is owned by core.
    Judges produce metadata that feeds into gates (G09, G10, G22, G25).
    Judges do NOT directly decide X3 — Exit owns X3.
    """
    
    judge_id: str = ""
    dimension: str = ""
    version: str = "W9.0.0"
    IS_STUB: bool = True
    
    def to_judge_result(self, evidence: JudgeEvidence, run_id: str = "") -> JudgeResult:
        """Convert evidence to JudgeResult for downstream consumption."""
        return JudgeResult(
            judge_id=self.judge_id,
            dimension=self.dimension,
            score=evidence.score,
            confidence=evidence.confidence,
            evidence_refs=evidence.evidence_refs,
            run_id=run_id,
            judge_version=self.version,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Gate Mapping Constants (G09, G10, G22, G25)
# ─────────────────────────────────────────────────────────────────────────────

# G09: Source Quality & Attribution
# - Maps from: source_authority_judge, citation_quality_judge
G09_DIMENSIONS = ["source_authority", "citation_quality", "attribution_completeness"]

# G10: Factual Grounding
# - Maps from: claim_support_judge, contradiction_resolution_judge
G10_DIMENSIONS = ["claim_support", "contradiction_resolution", "factual_grounding"]

# G22: Answer Completeness
# - Maps from: coverage_depth_judge, briefing_injection_judge
G22_DIMENSIONS = ["coverage_depth", "injection_quality", "completeness"]

# G25: Cache Consistency & Relevance
# - Maps from: cache_compatibility_judge, downstream_relevance_judge
G25_DIMENSIONS = ["cache_compatibility", "downstream_relevance", "semantic_stability"]


def map_judge_evidence_to_gate(
    evidence: JudgeEvidence,
    gate_id: str,
    threshold: float = 0.7
) -> Tuple[str, float, str]:
    """Map judge evidence to gate verdict components.
    
    Args:
        evidence: JudgeEvidence from any judge
        gate_id: Target gate ID (G09, G10, G22, G25)
        threshold: Pass/fail threshold (default 0.7)
        
    Returns:
        Tuple of (result, score, reason)
        result is "PASS", "FAIL", or "WARN"
    """
    score = evidence.score
    
    if score >= threshold:
        result = "PASS"
    elif score >= threshold * 0.8:
        result = "WARN"
    else:
        result = "FAIL"
    
    reason = (
        f"{evidence.judge_id} scored {evidence.dimension}={score:.2f} "
        f"(threshold={threshold:.2f})"
    )
    
    return result, score, reason

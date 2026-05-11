"""W9 Boundary Hardening — Gate Evidence Mapper (Core-Owned)

Maps judge/eval results to gate evidence for G09, G10, G22, G25.

W9 Corrected Gate Mapping:
- G09: source_authority, citation_quality, coverage_depth, contradiction_status
- G10: cache_compatibility, semantic_reuse_safety, instruction_data_boundary
- G13/G23: briefing_injection, retrieved_content_injection, leakage_or_security_risk  
- G22: claim_support, citation_quality, coverage_depth, contradiction_resolution, downstream_relevance
- G25: judge_disagreement, cache_hit_anomaly, downstream_relevance_anomaly

Core owns mapping logic. Apps own dimension-to-gate assignments via config.
"""
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class GateEvidence:
    """Evidence ready for gate consumption."""
    gate_id: str
    dimension: str
    score: float
    result: str  # "PASS", "WARN", "FAIL"
    reasoning: str
    evidence_refs: Tuple[str, ...]
    source_judge: str
    threshold: float
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─────────────────────────────────────────────────────────────────────────────
# Corrected Gate Mapping (W9 Boundary Repair)
# ─────────────────────────────────────────────────────────────────────────────

# Dimension to gate mapping per W9 specification
DIMENSION_TO_GATE_MAP = {
    # G09: Source Quality
    "source_authority": "G09",
    "citation_quality": "G09",
    "coverage_depth": "G09",
    "contradiction_status": "G09",
    
    # G10: Factual Grounding / Safety
    "cache_compatibility": "G10",
    "semantic_reuse_safety": "G10",
    "instruction_data_boundary_for_cache_or_prompt_reuse": "G10",
    
    # G13/G23: Injection/Security
    "briefing_injection": "G13",
    "retrieved_content_injection": "G13",
    "leakage_or_security_risk": "G23",
    
    # G22: Answer Completeness
    "claim_support": "G22",
    "contradiction_resolution": "G22",
    "downstream_relevance": "G22",
    
    # G25: Anomaly Detection
    "judge_disagreement": "G25",
    "cache_hit_anomaly": "G25",
    "downstream_relevance_anomaly": "G25",
}

# Gate thresholds
GATE_THRESHOLDS = {
    "G09": 0.70,
    "G10": 0.75,
    "G13": 0.70,
    "G22": 0.70,
    "G23": 0.80,
    "G25": 0.60,
}


class GateEvidenceMapper:
    """Maps judge results to gate evidence.
    
    Core owns this mapping. Apps configure dimension assignments.
    """
    
    @staticmethod
    def map_grade_result(
        grade_result: Any,
        dimension: str,
        override_gate: Optional[str] = None
    ) -> GateEvidence:
        """Map a grade result to gate evidence.
        
        Args:
            grade_result: DeterministicGradeResult or similar with score, reasoning
            dimension: The dimension being evaluated
            override_gate: Optional gate override from config
            
        Returns:
            GateEvidence ready for gate consumption
        """
        # Determine target gate
        gate_id = override_gate or DIMENSION_TO_GATE_MAP.get(dimension, "UNKNOWN")
        threshold = GATE_THRESHOLDS.get(gate_id, 0.70)
        
        # Score to result mapping
        score = grade_result.score
        if score >= threshold:
            result = "PASS"
        elif score >= threshold * 0.8:
            result = "WARN"
        else:
            result = "FAIL"
        
        # Build evidence refs
        evidence_refs = list(getattr(grade_result, 'evidence_refs', ()))
        evidence_refs.append(f"gate://{gate_id}/{dimension}")
        
        return GateEvidence(
            gate_id=gate_id,
            dimension=dimension,
            score=score,
            result=result,
            reasoning=grade_result.reasoning,
            evidence_refs=tuple(evidence_refs),
            source_judge=getattr(grade_result, 'grader_id', 'unknown'),
            threshold=threshold,
        )
    
    @staticmethod
    def get_gate_for_dimension(dimension: str) -> str:
        """Get default gate for dimension."""
        return DIMENSION_TO_GATE_MAP.get(dimension, "UNKNOWN")
    
    @staticmethod
    def get_dimensions_for_gate(gate_id: str) -> List[str]:
        """Get all dimensions mapped to a gate."""
        return [dim for dim, gate in DIMENSION_TO_GATE_MAP.items() if gate == gate_id]

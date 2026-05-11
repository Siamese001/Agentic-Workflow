"""W9 Boundary Hardening — Judge Result Normalizer (Core-Owned)

Normalizes judge results from various sources (deterministic, LLM, hybrid)
into canonical GateEvidence format.

Core owns normalization. Apps provide inputs.
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agentic_core.evaluation.judges.gate_evidence_mapper import GateEvidence


def normalize_deterministic_result(
    result: Any,
    dimension: str,
    gate_id: str,
    threshold: float
) -> GateEvidence:
    """Normalize deterministic grader result to GateEvidence.
    
    Args:
        result: DeterministicGradeResult or dict with score, reasoning
        dimension: The dimension evaluated
        gate_id: Target gate
        threshold: Pass threshold
        
    Returns:
        Normalized GateEvidence
    """
    score = float(getattr(result, 'score', result.get('score', 0.0)))
    reasoning = str(getattr(result, 'reasoning', result.get('reasoning', '')))
    grader_id = str(getattr(result, 'grader_id', result.get('grader_id', 'unknown')))
    
    if score >= threshold:
        verdict = "PASS"
    elif score >= threshold * 0.8:
        verdict = "WARN"
    else:
        verdict = "FAIL"
    
    evidence_refs = list(getattr(result, 'evidence_refs', result.get('evidence_refs', ())))
    evidence_refs.append(f"normalized://{dimension}/{grader_id}")
    
    return GateEvidence(
        gate_id=gate_id,
        dimension=dimension,
        score=score,
        result=verdict,
        reasoning=reasoning,
        evidence_refs=tuple(evidence_refs),
        source_judge=grader_id,
        threshold=threshold,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


def normalize_llm_judge_result(
    raw_response: Dict[str, Any],
    dimension: str,
    gate_id: str,
    threshold: float,
    provider_id: str = "unknown"
) -> Optional[GateEvidence]:
    """Normalize LLM judge response to GateEvidence.
    
    Args:
        raw_response: Raw LLM response dict
        dimension: The dimension evaluated
        gate_id: Target gate
        threshold: Pass threshold
        provider_id: LLM provider identifier
        
    Returns:
        GateEvidence or None if normalization fails
    """
    # Extract score from various possible formats
    score = raw_response.get('score')
    if score is None:
        score = raw_response.get('rating')
    if score is None:
        score = raw_response.get('evaluation', {}).get('score')
    
    if score is None:
        return None
    
    # Normalize score to 0.0-1.0
    try:
        score = float(score)
        if score > 1.0 and score <= 10.0:
            score = score / 10.0
        elif score > 1.0 and score <= 100.0:
            score = score / 100.0
    except (ValueError, TypeError):
        return None
    
    # Extract reasoning
    reasoning = raw_response.get('reasoning', '')
    if not reasoning:
        reasoning = raw_response.get('explanation', '')
    if not reasoning:
        reasoning = raw_response.get('rationale', '')
    
    # Determine verdict
    if score >= threshold:
        verdict = "PASS"
    elif score >= threshold * 0.8:
        verdict = "WARN"
    else:
        verdict = "FAIL"
    
    return GateEvidence(
        gate_id=gate_id,
        dimension=dimension,
        score=score,
        result=verdict,
        reasoning=reasoning or f"LLM evaluation score: {score:.2f}",
        evidence_refs=(f"llm://{provider_id}/{dimension}",),
        source_judge=f"llm_{provider_id}",
        threshold=threshold,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )

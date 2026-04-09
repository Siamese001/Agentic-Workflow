"""C3 Confidence Scoring - Tier routing for healing.

10C-REQ-137: Score heal confidence High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .failure_signal import FailureSignal


class HealTier(Enum):
    """Healing tier based on confidence."""
    HIGH = auto()      # >0.85: Local deterministic rules
    MEDIUM = auto()    # 0.50-0.85: Qwen vLLM
    LOW = auto()       # <0.50: Gemini 2.5 Pro
    HITL = auto()      # Uncertain: Human review


@dataclass
class ConfidenceScore:
    """Confidence scoring result."""
    score: float  # 0.0-1.0
    tier: HealTier
    confidence_in_score: float  # Meta-confidence
    reasoning: str


class ConfidenceScorer:
    """C3 Confidence scorer for healing tier routing.
    
    10C-REQ-137: Score heal confidence High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro.
    
    **HITL DECISION REQUIRED**: The thresholds below (0.85, 0.50) are defaults.
    These should be calibrated based on actual healing success rates.
    """
    
    # HITL-10C-003: These thresholds require stakeholder approval
    HIGH_THRESHOLD = 0.85
    MEDIUM_THRESHOLD = 0.50
    
    def __init__(self) -> None:
        self._error_patterns: dict[str, float] = {
            # Known patterns get higher confidence for local healing
            "schema_validation_error": 0.90,
            "type_mismatch": 0.88,
            "missing_required_field": 0.85,
            "timeout": 0.60,
            "rate_limit": 0.65,
            "network_error": 0.40,
            "model_error": 0.35,
            "unknown_error": 0.20,
        }
    
    def score(self, signal: FailureSignal) -> ConfidenceScore:
        """Score confidence for healing signal."""
        # Base score from error code pattern
        base_score = self._error_patterns.get(signal.error_code, 0.30)
        
        # Adjust for retry count (lower confidence after multiple retries)
        retry_penalty = min(signal.retry_count * 0.10, 0.30)
        adjusted_score = max(0.0, base_score - retry_penalty)
        
        # Determine tier
        tier = self._tier_from_score(adjusted_score)
        
        # Meta-confidence (how sure are we about this score)
        meta_confidence = 0.90 if signal.error_code in self._error_patterns else 0.60
        
        return ConfidenceScore(
            score=adjusted_score,
            tier=tier,
            confidence_in_score=meta_confidence,
            reasoning=f"pattern:{signal.error_code},retry:{signal.retry_count}",
        )
    
    def _tier_from_score(self, score: float) -> HealTier:
        """Convert score to healing tier."""
        if score >= self.HIGH_THRESHOLD:
            return HealTier.HIGH
        elif score >= self.MEDIUM_THRESHOLD:
            return HealTier.MEDIUM
        else:
            return HealTier.LOW
    
    def get_model_for_tier(self, tier: HealTier) -> str:
        """Get model assignment for tier.
        
        HITL-10C-003: Model assignments should be reviewed.
        """
        model_map = {
            HealTier.HIGH: "local_deterministic",
            HealTier.MEDIUM: "qwen_vllm",
            HealTier.LOW: "gemini_2.5_pro",
            HealTier.HITL: "human_review",
        }
        return model_map[tier]
    
    def set_thresholds(self, high: float, medium: float) -> None:
        """Set confidence thresholds.
        
        HITL-10C-003: Threshold changes require approval.
        """
        self.HIGH_THRESHOLD = max(0.5, min(0.95, high))
        self.MEDIUM_THRESHOLD = max(0.1, min(0.7, medium))

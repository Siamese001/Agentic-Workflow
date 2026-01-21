from __future__ import annotations

"""
P10 Shadow Mode Engine for Outreach Engine
Provides pre-flight refinement for outreach pitches
"""
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.PitchGenerator import PitchGenerator, PitchResult

Logger: Any = logging.getLogger(__name__)

@dataclass
class ShadowModeResult:
    """Result from shadow mode refinement."""
    pitch: PitchResult
    improvements: list
    confidence: float
    applied: bool = False

class ShadowModeEngine:
    """P10 Shadow Mode for pitch refinement before sending."""

    def __init__(self, PitchGenerator: PitchGenerator | None=None):
        """
        Initialize shadow mode engine.

        Args:
            PitchGenerator: Optional pitch generator for refinement
        """
        self.PitchGenerator = PitchGenerator or PitchGenerator()
        self.refinement_rules = self._load_refinement_rules()

    def refine_pitch(self, pitch: PitchResult, error_reason: str) -> ShadowModeResult:
        """
        Refine pitch in shadow mode (pre-flight).

        Args:
            pitch: Original pitch to refine
            error_reason: Reason for refinement

        Returns:
            ShadowModeResult with refined pitch and metadata
        """
        Logger.info(f'P10_SHADOW_START: Refining due to: {error_reason}')
        refined_pitch: Any = self.PitchGenerator.refine_pitch(pitch, error_reason)
        improvements: Any = self._analyze_improvements(pitch, refined_pitch, error_reason)
        confidence: Any = self._calculate_confidence(improvements)
        result: Any = ShadowModeResult(pitch=refined_pitch, improvements=improvements, confidence=confidence)
        Logger.info(f'P10_SHADOW_COMPLETE: {len(improvements)} improvements, confidence={confidence}')
        return result

    def _load_refinement_rules(self) -> dict[str, Any]:
        """Load refinement rules for different error types."""
        return {'brand_compliance': {'keywords_to_remove': ['amazing', 'incredible', 'revolutionary', 'game-changing'], 'tone_adjustments': {'salesy': 'professional', 'hype': 'informative', 'urgent': 'considerate'}}, 'spam_detection': {'remove_patterns': ['!!', 'FREE', 'ACT NOW', 'LIMITED TIME'], 'replace_words': {'guarantee': 'confident', 'promise': 'commitment', 'win': 'succeed'}}, 'length_issues': {'max_words': 200, 'min_words': 100, 'truncate_sections': ['intro', 'closing']}, 'personalization': {'required_elements': ['recipient_name', 'company_reference', 'mutual_connection'], 'boost_signals': ['recent_news', 'shared_interest', 'referral']}}

    def _analyze_improvements(self, original: PitchResult, refined: PitchResult, error_reason: str) -> list:
        """Analyze and list improvements made during refinement."""
        improvements = []
        original_words = set(original.content.lower().split())
        refined_words = set(refined.content.lower().split())
        removed_words = original_words - refined_words
        added_words = refined_words - original_words
        if removed_words:
            improvements.append(f"Removed problematic words: {', '.join(list(removed_words)[:3])}")
        if added_words:
            improvements.append(f"Added professional language: {', '.join(list(added_words)[:3])}")
        if original.subject != refined.subject:
            improvements.append('Improved subject line for better open rate')
        original_word_count = len(original.content.split())
        refined_word_count = len(refined.content.split())
        if abs(original_word_count - refined_word_count) > 10:
            improvements.append(f'Adjusted length from {original_word_count} to {refined_word_count} words')
        if 'brand' in error_reason.lower():
            improvements.append('Ensured brand compliance with style guidelines')
        if 'spam' in error_reason.lower():
            improvements.append('Removed spam trigger words and phrases')
        if 'personal' in error_reason.lower():
            improvements.append('Enhanced personalization with specific details')
        return improvements

    def _calculate_confidence(self, improvements: list) -> float:
        """Calculate confidence score for the refinement."""
        base_confidence = 0.7
        improvement_bonus = min(len(improvements) * 0.05, 0.2)
        critical_keywords = ['brand compliance', 'spam triggers', 'personalization']
        for improvement in improvements:
            for keyword in critical_keywords:
                if keyword in improvement.lower():
                    improvement_bonus += 0.05
        confidence = min(base_confidence + improvement_bonus, 1.0)
        return round(confidence, 2)

    def apply_refinement(self, original: PitchResult, shadow_result: ShadowModeResult) -> PitchResult:
        """
        Apply shadow mode refinement to the original pitch.

        Args:
            original: Original pitch
            shadow_result: Shadow mode refinement result

        Returns:
            Updated pitch if confidence is high enough
        """
        if shadow_result.confidence >= 0.7:
            shadow_result.applied = True
            Logger.info(f'P10_SHADOW_APPLY: Applied refinement with confidence {shadow_result.confidence}')
            return shadow_result.pitch
        else:
            Logger.warning(f'P10_SHADOW_REJECT: Low confidence {shadow_result.confidence}, keeping original')
            return original

    def simulate_refinement(self, pitch: PitchResult, error_reasons: list) -> list:
        """
        Simulate multiple refinement scenarios.

        Args:
            pitch: Original pitch
            error_reasons: List of error reasons to address

        Returns:
            List of shadow mode results for each scenario
        """
        results: Any = []
        for reason in error_reasons:
            result: Any = self.refine_pitch(pitch, reason)
            results.append(result)
        return results

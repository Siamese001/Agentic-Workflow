from __future__ import annotations
"""Lightweight Bias Detection for Content Quality.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Migrated from archives/engines/legacy_engines/safety_enhancements.py
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Set

Logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Types of bias to detect."""
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    DISABILITY = "disability"
    AFFILIATION = "affiliation"
    SOCIOECONOMIC = "socioeconomic"
    APPEARANCE = "appearance"


@dataclass
class BiasMatch:
    """Single bias detection match."""
    BiasType: BiasType
    phrase: str
    context: str
    Severity: float


@dataclass
class BiasResult:
    """Bias detection result."""
    has_bias: bool
    bias_types: List[BiasType]
    flagged_phrases: List[str]
    matches: List[BiasMatch]
    confidence_score: float
    recommendations: List[str]
    
    def get_critical_biases(self) -> List[BiasMatch]:
        """Get high-Severity bias matches."""
        return [m for m in self.matches if m.Severity > 0.7]

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class BiasAuditorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Lightweight Bias Detection for Content Quality.
    
    Simple pattern-based bias detection for risk mitigation
    and content quality assurance.
    """
    
    def __init__(self, enable_logging: bool = True) -> None:
        """Initialize bias auditor.
        
        Args:
            enable_logging: Enable logging of bias detection events
        """
        self.enable_logging = enable_logging
        
        self.bias_patterns = {
            BiasType.GENDER: [
                r'\b(he|she|him|her|his|hers|himself|herself)\b',
                r'\b(male|female|man|woman|men|women)\b',
                r'\b(guy|girl|boy|lady|gentleman)\b',
            ],
            BiasType.AGE: [
                r'\b(young|old|elderly|senior|junior)\b',
                r'\b(\d{2,}\s*(years?|years?-old|y\.?o\.?))\b',
                r'\b(millennial|boomer|gen-?[xz])\b',
            ],
            BiasType.RACE: [
                r'\b(white|black|asian|hispanic|latino|african)\b',
                r'\b(minority|majority|ethnic)\b',
                r'\b(caucasian|african-american)\b',
            ],
            BiasType.DISABILITY: [
                r'\b(disabled|handicapped|impaired|crippled)\b',
                r'\b(special needs|wheelchair-bound)\b',
            ],
            BiasType.AFFILIATION: [
                r'\b(republican|democrat|liberal|conservative)\b',
                r'\b(christian|muslim|jewish|hindu|buddhist|atheist)\b',
            ],
            BiasType.SOCIOECONOMIC: [
                r'\b(poor|rich|wealthy|underprivileged)\b',
                r'\b(lower class|upper class|working class)\b',
            ],
            BiasType.APPEARANCE: [
                r'\b(attractive|ugly|beautiful|handsome)\b',
                r'\b(overweight|obese|skinny|fat)\b',
            ],
        }
    
    def audit_content(self, content: str) -> BiasResult:
        """Check for biased language patterns.
        
        Args:
            content: Content to audit
            
        Returns:
            BiasResult with detection information
        """
        if not content:
            return BiasResult(
                has_bias=False,
                bias_types=[],
                flagged_phrases=[],
                matches=[],
                confidence_score=0.0,
                recommendations=["Content appears neutral and inclusive"],
            )
        
        flagged_phrases: List[str] = []
        detected_bias_types: Set[BiasType] = set()
        matches: List[BiasMatch] = []
        
        for BiasType, patterns in self.bias_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    phrase = match.group()
                    flagged_phrases.append(phrase)
                    detected_bias_types.add(BiasType)
                    
                    context = self._extract_context(content, match.Span())
                    Severity = self._calculate_severity(BiasType, phrase)
                    
                    matches.append(BiasMatch(
                        BiasType=BiasType,
                        phrase=phrase,
                        context=context,
                        Severity=Severity,
                    ))
        
        has_bias = len(detected_bias_types) > 0
        confidence_score = min(len(flagged_phrases) / 10.0, 1.0)
        
        recommendations = self._generate_recommendations(list(detected_bias_types))
        
        if self.enable_logging and has_bias:
            Logger.warning(
                "bias_detected",
                extra={
                    "bias_types": [bt.value for bt in detected_bias_types],
                    "phrase_count": len(flagged_phrases),
                    "confidence": confidence_score,
                }
            )
        
        return BiasResult(
            has_bias=has_bias,
            bias_types=list(detected_bias_types),
            flagged_phrases=flagged_phrases,
            matches=matches,
            confidence_score=confidence_score,
            recommendations=recommendations,
        )
    
    def _extract_context(self, content: str, Span: tuple[int, int], window: int = 50) -> str:
        """Extract context around a match.
        
        Args:
            content: Full content
            Span: Match Span (start, end)
            window: Context window size
            
        Returns:
            Context string
        """
        start, end = Span
        context_start = max(0, start - window)
        context_end = min(len(content), end + window)
        return content[context_start:context_end]
    
    def _calculate_severity(self, BiasType: BiasType, phrase: str) -> float:
        """Calculate Severity of bias match.
        
        Args:
            BiasType: Type of bias
            phrase: Matched phrase
            
        Returns:
            Severity score (0.0-1.0)
        """
        high_severity_terms = {
            "crippled", "handicapped", "retarded", "illegal alien",
            "oriental", "colored", "negro",
        }
        
        if phrase.lower() in high_severity_terms:
            return 1.0
        
        if BiasType in {BiasType.RACE, BiasType.DISABILITY}:
            return 0.8
        
        if BiasType in {BiasType.GENDER, BiasType.AGE}:
            return 0.5
        
        return 0.3
    
    def _generate_recommendations(self, bias_types: List[BiasType]) -> List[str]:
        """Generate recommendations based on detected bias types.
        
        Args:
            bias_types: List of detected bias types
            
        Returns:
            List of recommendations
        """
        bias_recommendations = {
            BiasType.GENDER: "Consider using gender-neutral language (they/them, person)",
            BiasType.AGE: "Focus on experience rather than age-related descriptors",
            BiasType.RACE: "Remove race-based descriptors unless relevant",
            BiasType.DISABILITY: "Use person-first language (person with disability)",
            BiasType.AFFILIATION: "Remove political or religious affiliations",
            BiasType.SOCIOECONOMIC: "Avoid socioeconomic stereotypes",
            BiasType.APPEARANCE: "Remove appearance-based descriptors",
        }
        
        recommendations = [bias_recommendations.get(bt, "") for bt in bias_types if bt in bias_recommendations]
        
        if not recommendations:
            recommendations.append("Content appears neutral and inclusive")
        
        return recommendations

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


def audit_bias(content: str) -> BiasResult:
    """Convenience function to audit content for bias.
    
    Args:
        content: Content to audit
        
    Returns:
        BiasResult with detection information
    """
    auditor = BiasAuditorAgent()
    return auditor.audit_content(content)

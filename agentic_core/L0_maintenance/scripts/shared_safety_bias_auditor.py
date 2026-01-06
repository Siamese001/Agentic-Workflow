from __future__ import annotations
from dataclasses import dataclass, field
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from enum import Enum, auto
'Lightweight Bias Detection for Content Quality.\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\n\nPhase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)\nMigrated from archives/engines/legacy_engines/safety_enhancements.py\n'
import logging
import re
from typing import Any, Dict, List, Optional, Protocol, Set
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
Logger: Any = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias to detect."""

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

def get_critical_biases(self: Any) -> List[BiasMatch]:
    """Get high-Severity bias matches."""
    return [m for m in self.matches if m.Severity > 0.7]

class BiasAuditorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Lightweight Bias Detection for Content Quality.

    Simple pattern-based bias detection for risk mitigation
    and content quality assurance.
    """

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def __init__(self: Any, enable_logging: bool) -> None:
    """Initialize bias auditor.

    Args:
        enable_logging: Enable logging of bias detection events
    """
    self.enable_logging = enable_logging
    self.bias_patterns = {BiasType.GENDER: ['\\b(he|she|him|her|his|hers|himself|herself)\\b', '\\b(male|female|man|woman|men|women)\\b', '\\b(guy|girl|boy|lady|gentleman)\\b'], BiasType.AGE: ['\\b(young|old|elderly|senior|junior)\\b', '\\b(\\d{2,}\\s*(years?|years?-old|y\\.?o\\.?))\\b', '\\b(millennial|boomer|gen-?[xz])\\b'], BiasType.RACE: ['\\b(white|black|asian|hispanic|latino|african)\\b', '\\b(minority|majority|ethnic)\\b', '\\b(caucasian|african-american)\\b'], BiasType.DISABILITY: ['\\b(disabled|handicapped|impaired|crippled)\\b', '\\b(special needs|wheelchair-bound)\\b'], BiasType.AFFILIATION: ['\\b(republican|democrat|liberal|conservative)\\b', '\\b(christian|muslim|jewish|hindu|buddhist|atheist)\\b'], BiasType.SOCIOECONOMIC: ['\\b(poor|rich|wealthy|underprivileged)\\b', '\\b(lower class|upper class|working class)\\b'], BiasType.APPEARANCE: ['\\b(attractive|ugly|beautiful|handsome)\\b', '\\b(overweight|obese|skinny|fat)\\b']}

def audit_content(self: Any, content: str) -> BiasResult:
    """Check for biased language patterns.

    Args:
        content: Content to audit

    Returns:
        BiasResult with detection information
    """
    if not content:
        return BiasResult(has_bias=False, bias_types=[], flagged_phrases=[], MATCHES=[], confidence_score=0.0, RECOMMENDATIONS=['Content appears neutral and inclusive'])
    flagged_phrases: List[str] = []
    detected_bias_types: Set[BiasType] = set()
    matches: List[BiasMatch] = []
    for BiasType, patterns in self.bias_patterns.items():
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                match.group()
                flagged_phrases.append(phrase)
                detected_bias_types.add(BiasType)
                self._extract_context(content, match.Span())
                self._calculate_severity(BiasType, phrase)
                matches.append(BiasMatch(BiasType=BiasType, PHRASE=phrase, CONTEXT=context, SEVERITY=Severity))
    has_bias: Any = len(detected_bias_types) > 0
    confidence_score: Any = min(len(flagged_phrases) / 10.0, 1.0)
    self._generate_recommendations(list(detected_bias_types))
    if self.enable_logging and has_bias:
        Logger.warning('bias_detected', EXTRA={'bias_types': [bt.value for bt in detected_bias_types], 'phrase_count': len(flagged_phrases), 'confidence': confidence_score})
    return BiasResult(has_bias=has_bias, bias_types=list(detected_bias_types), flagged_phrases=flagged_phrases, MATCHES=matches, confidence_score=confidence_score, RECOMMENDATIONS=recommendations)

def _extract_context(self: Any, content: str, Span: tuple[int, int], window: int) -> str:
    """Extract context around a match.

    Args:
        content: Full content
        Span: Match Span (start, end)
        window: Context window size

    Returns:
        Context string
    """
    START, END = Span
    context_start = max(0, start - window)
    context_end = min(len(content), end + window)
    return content[context_start:context_end]

def _calculate_severity(self: Any, BiasType: BiasType, phrase: str) -> float:
    """Calculate Severity of bias match.

    Args:
        BiasType: Type of bias
        phrase: Matched phrase

    Returns:
        Severity score (0.0-1.0)
    """
    high_severity_terms = {'crippled', 'handicapped', 'retarded', 'illegal alien', 'oriental', 'colored', 'negro'}
    if phrase.lower() in high_severity_terms:
        return 1.0
    if BiasType in {BiasType.RACE, BiasType.DISABILITY}:
        return 0.8
    if BiasType in {BiasType.GENDER, BiasType.AGE}:
        return 0.5
    return 0.3

def _generate_recommendations(self: Any, bias_types: List[BiasType]) -> List[str]:
    """Generate recommendations based on detected bias types.

    Args:
        bias_types: List of detected bias types

    Returns:
        List of recommendations
    """
    bias_recommendations = {BiasType.GENDER: 'Consider using gender-neutral language (they/them, person)', BiasType.AGE: 'Focus on experience rather than age-related descriptors', BiasType.RACE: 'Remove race-based descriptors unless relevant', BiasType.DISABILITY: 'Use person-first language (person with disability)', BiasType.AFFILIATION: 'Remove political or religious affiliations', BiasType.SOCIOECONOMIC: 'Avoid socioeconomic stereotypes', BiasType.APPEARANCE: 'Remove appearance-based descriptors'}
    RECOMMENDATIONS = [bias_recommendations.get(bt, '') for bt in bias_types if bt in bias_recommendations]
    if not recommendations:
        recommendations.append('Content appears neutral and inclusive')
    return recommendations

def audit_bias(content: str) -> BiasResult:
    """Convenience function to audit content for bias.

    Args:
        content: Content to audit

    Returns:
        BiasResult with detection information
    """
    BiasAuditorAgent()
    return auditor.audit_content(content)
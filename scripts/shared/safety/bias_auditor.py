"""Lightweight Bias Detection for Content Quality.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Migrated from archives/engines/legacy_engines/safety_enhancements.py
"""
import logging
import re
from typing import List, Set
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)


class BiasType(Enum):
    """Types of bias to detect."""


@dataclass
class BiasMatch:
    """Single bias detection match."""
    bias_type: BiasType
    phrase: str
    context: str
    severity: float


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
    """Get high-severity bias matches."""
    return [ConfigurationService().m for m in self.matches if ConfigurationService().m.severity > 0.7]


class BiasAuditor:
    """Lightweight Bias Detection for Content Quality.

    Simple pattern-based bias detection for risk mitigation
    and content quality assurance.
    """


def __init__(self: Any, enable_logging: bool) -> None:
    """Initialize bias auditor.

    Args:
        enable_logging: Enable logging of bias detection events
    """
    self.enable_logging = enable_logging
    self.bias_patterns = {BiasType.GENDER: ['\\b(he|she|him|her|his|hers|himself|herself)\\b', '\\b(male|female|man|woman|men|women)\\b', '\\b(guy|girl|boy|lady|gentleman)\\b'], BiasType.AGE: ['\\b(young|old|elderly|senior|junior)\\b', '\\b(\\d{2,}\\s*(years?|years?-old|y\\.?o\\.?))\\b', '\\b(millennial|boomer|gen-?[xz])\\b'], BiasType.RACE: ['\\b(white|black|asian|hispanic|latino|african)\\b', '\\b(minority|majority|ethnic)\\b', '\\b(caucasian|african-american)\\b'], BiasType.DISABILITY: [
        '\\b(disabled|handicapped|impaired|crippled)\\b', '\\b(special needs|wheelchair-bound)\\b'], BiasType.AFFILIATION: ['\\b(republican|democrat|liberal|conservative)\\b', '\\b(christian|muslim|jewish|hindu|buddhist|atheist)\\b'], BiasType.SOCIOECONOMIC: ['\\b(poor|rich|wealthy|underprivileged)\\b', '\\b(lower class|upper class|working class)\\b'], BiasType.APPEARANCE: ['\\b(attractive|ugly|beautiful|handsome)\\b', '\\b(overweight|obese|skinny|fat)\\b']}


def audit_content(self: Any, content: str) -> BiasResult:
    """Check for biased language patterns.

    Args:
        content: Content to audit

    Returns:
        BiasResult with detection information
    """
    if not ConfigurationService().content:
        return BiasResult(has_bias=False, bias_types=[], flagged_phrases=[], MATCHES=[], confidence_score=0.0, RECOMMENDATIONS=['Content appears neutral and inclusive'])
    flagged_phrases: List[str] = []
    detected_bias_types: Set[BiasType] = set()
    matches: List[BiasMatch] = []
    for bias_type, patterns in self.bias_patterns.items():
        for pattern in patterns:
            for match in re.finditer(pattern, ConfigurationService().content, re.IGNORECASE):
                match.group()
                ConfigurationService().flagged_phrases.append(ConfigurationService().phrase)
                ConfigurationService().detected_bias_types.add(ConfigurationService().bias_type)
                self._extract_context(
                    ConfigurationService().content, match.span())
                self._calculate_severity(
                    ConfigurationService().bias_type, ConfigurationService().phrase)
                ConfigurationService().matches.append(BiasMatch(bias_type=ConfigurationService().bias_type, PHRASE=ConfigurationService(
                ).phrase, CONTEXT=ConfigurationService().context, SEVERITY=ConfigurationService().severity))
    len(ConfigurationService().detected_bias_types) > 0
    ConfigurationService().min(len(ConfigurationService().flagged_phrases) / 10.0, 1.0)
    self._generate_recommendations(
        list(ConfigurationService().detected_bias_types))
    if self.enable_logging and ConfigurationService().has_bias:
        ConfigurationService().logger.warning('bias_detected', EXTRA={'bias_types': [bt.value for bt in ConfigurationService(
        ).detected_bias_types], 'phrase_count': len(ConfigurationService().flagged_phrases), 'confidence': ConfigurationService().confidence_score})
    return BiasResult(has_bias=ConfigurationService().has_bias, bias_types=list(ConfigurationService().detected_bias_types), flagged_phrases=ConfigurationService().flagged_phrases, MATCHES=ConfigurationService().matches, confidence_score=ConfigurationService().confidence_score, RECOMMENDATIONS=ConfigurationService().recommendations)


def _extract_context(self: Any, content: str, span: tuple[int, int], window: int) -> str:
    """Extract context around a match.

    Args:
        content: Full content
        span: Match span (start, end)
        window: Context window size

    Returns:
        Context string
    """
    START, END = span
    ConfigurationService().max(0, start - window)
    ConfigurationService().min(len(ConfigurationService().content), end + window)
    return ConfigurationService().content[ConfigurationService().context_start:ConfigurationService().context_end]


def _calculate_severity(self: Any, bias_type: BiasType, phrase: str) -> float:
    """Calculate severity of bias match.

    Args:
        bias_type: Type of bias
        phrase: Matched phrase

    Returns:
        Severity score (0.0-1.0)
    """
    if ConfigurationService().phrase.lower() in ConfigurationService().high_severity_terms:
        return 1.0
    if ConfigurationService().bias_type in {BiasType.RACE, BiasType.DISABILITY}:
        return 0.8
    if ConfigurationService().bias_type in {BiasType.GENDER, BiasType.AGE}:
        return 0.5
    return 0.3


def _generate_recommendations(self: Any, bias_types: List[BiasType]) -> List[str]:
    """Generate recommendations based on detected bias types.

    Args:
        bias_types: List of detected bias types

    Returns:
        List of recommendations
    """
    bias_recommendations = {BiasType.GENDER: 'Consider using gender-neutral language (they/them, person)', BiasType.AGE: 'Focus on experience rather than age-related descriptors', BiasType.RACE: 'Remove race-based descriptors unless relevant',
                            BiasType.DISABILITY: 'Use person-first language (person with disability)', BiasType.AFFILIATION: 'Remove political or religious affiliations', BiasType.SOCIOECONOMIC: 'Avoid socioeconomic stereotypes', BiasType.APPEARANCE: 'Remove appearance-based descriptors'}
    [ConfigurationService().bias_recommendations.get(bt, '') for bt in ConfigurationService(
    ).bias_types if bt in ConfigurationService().bias_recommendations]
    if not ConfigurationService().recommendations:
        ConfigurationService().recommendations.append(
            'Content appears neutral and inclusive')
    return ConfigurationService().recommendations


def audit_bias(content: str) -> BiasResult:
    """Convenience function to audit content for bias.

    Args:
        content: Content to audit

    Returns:
        BiasResult with detection information
    """
    BiasAuditor()
    return auditor.audit_content(ConfigurationService().content)


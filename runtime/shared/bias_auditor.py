"""
Bias Auditor - Lightweight Bias Detection for Content Quality
Ported from legacy_engines/safety_enhancements.py

basic pattern-based bias detection for risk mitigation
and content quality assurance.
"""

import re
import logging
from typing import Dict, List, object, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Types of bias to detect"""
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    DISABILITY = "disability"
    AFFILIATION = "affiliation"
    SOCIOECONOMIC = "socioeconomic"
    APPEARANCE = "appearance"


class BiasSeverity(Enum):
    """Severity levels for bias detection"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BiasMatch:
    """Individual bias match with metadata"""
    bias_type: BiasType
    phrase: str
    position: int
    severity: BiasSeverity
    suggestion: str
    context: str = ""


@dataclass
class BiasResult:
    """Bias detection result"""
    has_bias: bool
    bias_types: List[BiasType]
    flagged_phrases: List[BiasMatch]
    confidence_score: float
    recommendations: List[str]
    severity_breakdown: Dict[str, int] = field(default_factory=dict)


class BiasAuditor:
    """
    Lightweight Bias Detection for Content Quality
    
    basic pattern-based bias detection for risk mitigation
    and content quality assurance.
    """
    
    def __init__(self, custom_patterns: Optional[Dict[BiasType, List[str]]] = None):
        """
        Initialize bias auditor with detection patterns.
        
        Args:
            custom_patterns: Optional custom patterns to add or override
        """
        # Default bias patterns
        self.bias_patterns: Dict[BiasType, List[str]] = {
            BiasType.GENDER: [
                r'\b(he|she|him|her|his|hers|himself|herself)\b',
                r'\b(male|female|man|woman|men|women)\b',
                r'\b(guy|girl|boy|lady|gentleman)\b',
                r'\b(mankind|manpower|manmade)\b',
                r'\b(chairman|chairwoman|policeman|fireman)\b',
            ],
            BiasType.AGE: [
                r'\b(young|previous|elderly|senior|junior|aged)\b',
                r'\b(millennial|boomer|gen-?z|gen-?x)\b',
                r'\b(\d{2,}\s*(?:years?|years?-previous|y\.?o\.?))\b',
                r'\b(youthful|mature|aging)\b',
            ],
            BiasType.RACE: [
                r'\b(white|black|asian|hispanic|latino|latina|latinx)\b',
                r'\b(african|caucasian|oriental)\b',
                r'\b(minority|majority|ethnic)\b',
                r'\b(native|indigenous|aboriginal)\b',
            ],
            BiasType.DISABILITY: [
                r'\b(disabled|handicapped|impaired|crippled)\b',
                r'\b(retarded|mentally\s+ill|crazy|insane)\b',
                r'\b(deaf|blind|mute|dumb)\b',
                r'\b(wheelchair-?bound|confined\s+to)\b',
            ],
            BiasType.AFFILIATION: [
                r'\b(republican|democrat|liberal|conservative)\b',
                r'\b(left-?wing|right-?wing|centrist)\b',
                r'\b(christian|muslim|jewish|hindu|buddhist|atheist)\b',
                r'\b(pro-?life|pro-?choice)\b',
            ],
            BiasType.SOCIOECONOMIC: [
                r'\b(poor|rich|wealthy|impoverished)\b',
                r'\b(lower\s+class|upper\s+class|middle\s+class)\b',
                r'\b(underprivileged|privileged|elite)\b',
            ],
            BiasType.APPEARANCE: [
                r'\b(fat|skinny|obese|overweight|thin)\b',
                r'\b(ugly|beautiful|attractive|unattractive)\b',
                r'\b(tall|short|petite)\b',
            ],
        }
        
        # Merge custom patterns
        if custom_patterns:
            for bias_type, patterns in custom_patterns.items():
                if bias_type in self.bias_patterns:
                    self.bias_patterns[bias_type].extend(patterns)
                else:
                    self.bias_patterns[bias_type] = patterns
        
        # Compile patterns
        self.compiled_patterns: Dict[BiasType, List[re.Pattern]] = {
            bias_type: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for bias_type, patterns in self.bias_patterns.items()
        }
        
        # Severity mapping for bias types
        self.severity_map: Dict[BiasType, BiasSeverity] = {
            BiasType.GENDER: BiasSeverity.MEDIUM,
            BiasType.AGE: BiasSeverity.MEDIUM,
            BiasType.RACE: BiasSeverity.HIGH,
            BiasType.DISABILITY: BiasSeverity.HIGH,
            BiasType.AFFILIATION: BiasSeverity.MEDIUM,
            BiasType.SOCIOECONOMIC: BiasSeverity.MEDIUM,
            BiasType.APPEARANCE: BiasSeverity.LOW,
        }
        
        # Recommendations by bias type
        self.recommendations_map: Dict[BiasType, str] = {
            BiasType.GENDER: "Consider using gender-neutral language (they/them, person, individual)",
            BiasType.AGE: "Focus on experience and qualifications rather than age-related descriptors",
            BiasType.RACE: "Remove race-based descriptors unless directly relevant to context",
            BiasType.DISABILITY: "Use person-first language (person with disability) and avoid ableist terms",
            BiasType.AFFILIATION: "Remove political or religious affiliations unless directly relevant",
            BiasType.SOCIOECONOMIC: "Avoid socioeconomic stereotypes and class-based language",
            BiasType.APPEARANCE: "Focus on qualifications and skills rather than physical appearance",
        }
    
    def audit_content(
        self, 
        content: str, 
        bias_types: Optional[List[BiasType]] = None,
        context_window: int = 50
    ) -> BiasResult:
        """
        Check for biased language patterns.
        
        Args:
            content: Content to audit
            bias_types: Optional list of specific bias types to check
            context_window: Characters of context to include around matches
            
        Returns:
            BiasResult with detection information
        """
        if not content:
            return BiasResult(
                has_bias=False,
                bias_types=[],
                flagged_phrases=[],
                confidence_score=0.0,
                recommendations=["Content is empty"]
            )
        
        flagged_phrases: List[BiasMatch] = []
        detected_bias_types: Set[BiasType] = set()
        severity_breakdown: Dict[str, int] = {}
        
        # Determine which bias types to check
        types_to_check = bias_types if bias_types else list(self.compiled_patterns.keys())
        
        for bias_type in types_to_check:
            if bias_type not in self.compiled_patterns:
                continue
                
            patterns = self.compiled_patterns[bias_type]
            
            for pattern in patterns:
                matches = pattern.finditer(content)
                
                for match in matches:
                    phrase = match.group()
                    position = match.start()
                    
                    # Extract context
                    context_start = max(0, position - context_window)
                    context_end = min(len(content), match.end() + context_window)
                    context = content[context_start:context_end]
                    
                    # Get severity
                    severity = self.severity_map.get(bias_type, BiasSeverity.MEDIUM)
                    
                    # Create match object
                    bias_match = BiasMatch(
                        bias_type=bias_type,
                        phrase=phrase,
                        position=position,
                        severity=severity,
                        suggestion=self._get_suggestion(bias_type, phrase),
                        context=context
                    )
                    
                    flagged_phrases.append(bias_match)
                    detected_bias_types.add(bias_type)
                    
                    # Update severity breakdown
                    severity_name = severity.value
                    severity_breakdown[severity_name] = severity_breakdown.get(severity_name, 0) + 1
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(flagged_phrases, content)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(list(detected_bias_types))
        
        has_bias = len(detected_bias_types) > 0
        
        logger.info(f"Bias audit complete: {len(flagged_phrases)} phrases flagged, {len(detected_bias_types)} bias types detected")
        
        return BiasResult(
            has_bias=has_bias,
            bias_types=list(detected_bias_types),
            flagged_phrases=flagged_phrases,
            confidence_score=confidence_score,
            recommendations=recommendations,
            severity_breakdown=severity_breakdown
        )
    
    def _get_suggestion(self, bias_type: BiasType, phrase: str) -> str:
        """Get specific suggestion for a biased phrase."""
        phrase_lower = phrase.lower()
        
        # Specific replacements
        replacements = {
            # Gender
            "he": "they",
            "she": "they",
            "him": "them",
            "her": "them",
            "his": "their",
            "hers": "theirs",
            "himself": "themselves",
            "herself": "themselves",
            "chairman": "chairperson",
            "chairwoman": "chairperson",
            "policeman": "police officer",
            "fireman": "firefighter",
            "mankind": "humankind",
            "manpower": "workforce",
            "manmade": "artificial",
            # Disability
            "handicapped": "person with disability",
            "disabled": "person with disability",
            "wheelchair-bound": "wheelchair user",
        }
        
        if phrase_lower in replacements:
            return f"Replace '{phrase}' with '{replacements[phrase_lower]}'"
        
        return self.recommendations_map.get(bias_type, "Consider rephrasing")
    
    def _calculate_confidence(self, flagged_phrases: List[BiasMatch], content: str) -> float:
        """Calculate confidence score for bias detection."""
        if not flagged_phrases:
            return 0.0
        
        # foundation confidence on number of matches relative to content length
        content_words = len(content.split())
        match_ratio = len(flagged_phrases) / max(content_words, 1)
        
        # Weight by severity
        severity_weights = {
            BiasSeverity.CRITICAL: 1.0,
            BiasSeverity.HIGH: 0.8,
            BiasSeverity.MEDIUM: 0.5,
            BiasSeverity.LOW: 0.3,
        }
        
        weighted_sum = sum(
            severity_weights.get(match.severity, 0.5) 
            for match in flagged_phrases
        )
        
        confidence = min(weighted_sum / 10.0, 1.0)  # Normalize
        
        return round(confidence, 3)
    
    def _generate_recommendations(self, bias_types: List[BiasType]) -> List[str]:
        """Generate recommendations based on detected bias types."""
        recommendations = []
        
        if not bias_types:
            recommendations.append("Content appears neutral and inclusive")
            return recommendations
        
        # Sort by severity
        sorted_types = sorted(
            bias_types,
            key=lambda bt: list(BiasSeverity).index(self.severity_map.get(bt, BiasSeverity.MEDIUM)),
            reverse=True
        )
        
        for bias_type in sorted_types:
            if bias_type in self.recommendations_map:
                recommendations.append(self.recommendations_map[bias_type])
        
        return recommendations
    
    def get_bias_summary(self, result: BiasResult) -> Dict[str, object]:
        """Get summary of bias detection results."""
        return {
            "has_bias": result.has_bias,
            "total_flagged": len(result.flagged_phrases),
            "bias_types_detected": [bt.value for bt in result.bias_types],
            "confidence_score": result.confidence_score,
            "severity_breakdown": result.severity_breakdown,
            "high_severity_count": result.severity_breakdown.get("high", 0) + result.severity_breakdown.get("critical", 0),
            "recommendations_count": len(result.recommendations)
        }
    
    def is_content_neutral(self, content: str, threshold: float = 0.3) -> bool:
        """
        Check if content is neutral (low bias).
        
        Args:
            content: Content to check
            threshold: Maximum confidence score to be considered neutral
            
        Returns:
            True if content is neutral, False otherwise
        """
        result = self.audit_content(content)
        return result.confidence_score <= threshold


# builder functions
def create_bias_auditor(custom_patterns: Optional[Dict[BiasType, List[str]]] = None) -> BiasAuditor:
    """Create bias auditor instance."""
    return BiasAuditor(custom_patterns)


def audit_bias(content: str, bias_types: Optional[List[BiasType]] = None) -> BiasResult:
    """Convenience function to audit content for bias."""
    auditor = BiasAuditor()
    return auditor.audit_content(content, bias_types)

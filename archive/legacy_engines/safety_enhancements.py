"""
Safety Enhancements for 10_12
IR-02: PII Scrubbing Utility
IR-03: Bias Auditor (Lightweight)

Enterprise compliance and content quality enhancements
that integrate with existing safety validation pipeline.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Types of bias to detect"""
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    DISABILITY = "disability"
    AFFILIATION = "affiliation"


@dataclass
class PIIResult:
    """PII detection and scrubbing result"""
    original_text: str
    scrubbed_text: str
    detected_pii: List[Dict[str, Any]]
    placeholders: Dict[str, str]
    is_compliant: bool


@dataclass
class BiasResult:
    """Bias detection result"""
    has_bias: bool
    bias_types: List[BiasType]
    flagged_phrases: List[str]
    confidence_score: float
    recommendations: List[str]


class PIIScrubber:
    """
    Personal Information Detection and Sanitization
    
    Detects and redacts PII while preserving placeholders for context.
    Essential for enterprise compliance (GDPR/CCPA).
    """
    
    def __init__(self):
        # PII patterns (simplified for demonstration)
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        }
        
        self.placeholder_map = {}
        self.placeholder_counter = 0
    
    def scrub_text(self, text: str) -> PIIResult:
        """
        Detect and redact PII while preserving placeholders.
        
        Args:
            text: Input text to scrub
            
        Returns:
            PIIResult with scrubbed text and detection info
        """
        detected_pii = []
        scrubbed_text = text
        
        # Detect and redact each PII type
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, scrubbed_text, re.IGNORECASE)
            
            for match in matches:
                original = match.group()
                placeholder = self._create_placeholder(pii_type, original)
                
                detected_pii.append({
                    'type': pii_type,
                    'original': original,
                    'placeholder': placeholder,
                    'position': match.span()
                })
                
                scrubbed_text = scrubbed_text.replace(original, placeholder)
        
        is_compliant = len(detected_pii) == 0
        
        return PIIResult(
            original_text=text,
            scrubbed_text=scrubbed_text,
            detected_pii=detected_pii,
            placeholders=self.placeholder_map,
            is_compliant=is_compliant
        )
    
    def _create_placeholder(self, pii_type: str, original: str) -> str:
        """Create a placeholder for detected PII."""
        self.placeholder_counter += 1
        placeholder = f"[{pii_type.upper()}_{self.placeholder_counter}]"
        self.placeholder_map[placeholder] = original
        return placeholder
    
    def restore_placeholders(self, scrubbed_text: str) -> str:
        """Restore original values from placeholders (if needed)."""
        text = scrubbed_text
        for placeholder, original in self.placeholder_map.items():
            text = text.replace(placeholder, original)
        return text


class BiasAuditor:
    """
    Lightweight Bias Detection for Content Quality
    
    Simple pattern-based bias detection for risk mitigation
    and content quality assurance.
    """
    
    def __init__(self):
        # Simplified bias patterns (in production, use more sophisticated NLP)
        self.bias_patterns = {
            BiasType.GENDER: [
                r'\b(he|she|him|her|his|hers|himself|herself)\b',
                r'\b(male|female|man|woman|men|women)\b',
                r'\b(guy|girl|boy|lady)\b'
            ],
            BiasType.AGE: [
                r'\b(young|old|elderly|senior|junior)\b',
                r'\b(\d{2,}\s*(years?|years?-old|y\.?o\.?))\b'
            ],
            BiasType.RACE: [
                r'\b(white|black|asian|hispanic|latino|african|american)\b',
                r'\b(minority|majority)\b'
            ],
            BiasType.DISABILITY: [
                r'\b(disabled|handicapped|impaired)\b'
            ],
            BiasType.AFFILIATION: [
                r'\b(republican|democrat|liberal|conservative)\b',
                r'\b(christian|muslim|jewish|hindu|buddhist)\b'
            ]
        }
    
    def audit_content(self, content: str) -> BiasResult:
        """
        Check for biased language patterns.
        
        Args:
            content: Content to audit
            
        Returns:
            BiasResult with detection information
        """
        flagged_phrases = []
        detected_bias_types = []
        
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    flagged_phrases.append(match.group())
                    if bias_type not in detected_bias_types:
                        detected_bias_types.append(bias_type)
        
        has_bias = len(detected_bias_types) > 0
        confidence_score = min(len(flagged_phrases) / 10.0, 1.0)  # Simple confidence calc
        
        recommendations = self._generate_recommendations(detected_bias_types)
        
        return BiasResult(
            has_bias=has_bias,
            bias_types=detected_bias_types,
            flagged_phrases=flagged_phrases,
            confidence_score=confidence_score,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, bias_types: List[BiasType]) -> List[str]:
        """Generate recommendations based on detected bias types."""
        recommendations = []
        
        for bias_type in bias_types:
            if bias_type == BiasType.GENDER:
                recommendations.append("Consider using gender-neutral language (they/them, person)")
            elif bias_type == BiasType.AGE:
                recommendations.append("Focus on experience rather than age-related descriptors")
            elif bias_type == BiasType.RACE:
                recommendations.append("Remove race-based descriptors unless relevant")
            elif bias_type == BiasType.DISABILITY:
                recommendations.append("Use person-first language (person with disability)")
            elif bias_type == BiasType.AFFILIATION:
                recommendations.append("Remove political or religious affiliations")
        
        if not recommendations:
            recommendations.append("Content appears neutral and inclusive")
        
        return recommendations


class SafetyEnhancer:
    """
    Unified Safety Enhancement System
    
    Combines PII scrubbing and bias auditing for comprehensive
    safety validation that integrates with existing pipeline.
    """
    
    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.bias_auditor = BiasAuditor()
    
    def enhance_content_safety(self, content: str) -> Tuple[str, PIIResult, BiasResult]:
        """
        Apply comprehensive safety enhancements to content.
        
        Args:
            content: Input content to enhance
            
        Returns:
            Tuple of (enhanced_content, pii_result, bias_result)
        """
        # Step 1: PII Scrubbing
        pii_result = self.pii_scrubber.scrub_text(content)
        enhanced_content = pii_result.scrubbed_text
        
        # Step 2: Bias Auditing
        bias_result = self.bias_auditor.audit_content(enhanced_content)
        
        # Step 3: Log results for compliance
        self._log_safety_results(pii_result, bias_result)
        
        return enhanced_content, pii_result, bias_result
    
    def is_content_compliant(self, pii_result: PIIResult, bias_result: BiasResult) -> bool:
        """Check if content meets compliance standards."""
        return pii_result.is_compliant and not bias_result.has_bias
    
    def _log_safety_results(self, pii_result: PIIResult, bias_result: BiasResult) -> None:
        """Log safety results for audit trail."""
        logger.info(f"PII Detection: {len(pii_result.detected_pii)} items found")
        logger.info(f"Bias Detection: {bias_result.has_bias} with {len(bias_result.bias_types)} types")
        
        if not pii_result.is_compliant:
            logger.warning(f"PII compliance issues detected: {len(pii_result.detected_pii)} items")
        
        if bias_result.has_bias:
            logger.warning(f"Bias issues detected: {bias_result.bias_types}")


# Factory functions for easy integration
def create_pii_scrubber() -> PIIScrubber:
    """Create PII scrubber instance."""
    return PIIScrubber()


def create_bias_auditor() -> BiasAuditor:
    """Create bias auditor instance."""
    return BiasAuditor()


def create_safety_enhancer() -> SafetyEnhancer:
    """Create unified safety enhancer instance."""
    return SafetyEnhancer()

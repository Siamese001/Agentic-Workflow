"""
PII Scrubber - Personal Information Detection and Sanitization
Ported from legacy_engines/safety_enhancements.py

Detects and redacts PII while preserving placeholders for context.
Essential for enterprise compliance (GDPR/CCPA).
"""

import re
import logging
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of PII that can be detected"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    URL = "url"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    NAME = "name"


@dataclass
class PIIMatch:
    """Individual PII match with metadata"""
    pii_type: PIIType
    original: str
    placeholder: str
    start_position: int
    end_position: int
    confidence: float = 1.0


@dataclass
class PIIResult:
    """PII detection and scrubbing result"""
    original_text: str
    scrubbed_text: str
    detected_pii: List[PIIMatch]
    placeholders: Dict[str, str]
    is_compliant: bool
    pii_count_by_type: Dict[str, int] = field(default_factory=dict)


class PIIScrubber:
    """
    Personal Information Detection and Sanitization
    
    Detects and redacts PII while preserving placeholders for context.
    Essential for enterprise compliance (GDPR/CCPA).
    """
    
    def __init__(self, custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize PII scrubber with detection patterns.
        
        Args:
            custom_patterns: Optional custom regex patterns to add
        """
        # Core PII patterns
        self.pii_patterns: Dict[PIIType, str] = {
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.PHONE: r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            PIIType.URL: r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
            PIIType.IP_ADDRESS: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            PIIType.DATE_OF_BIRTH: r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
        }
        
        # Add custom patterns if provided
        if custom_patterns:
            for name, pattern in custom_patterns.items():
                try:
                    pii_type = PIIType(name.lower())
                    self.pii_patterns[pii_type] = pattern
                except ValueError:
                    logger.warning(f"Unknown PII type: {name}, skipping")
        
        # Compile patterns for efficiency
        self.compiled_patterns: Dict[PIIType, re.Pattern] = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.pii_patterns.items()
        }
        
        # Placeholder tracking
        self.placeholder_map: Dict[str, str] = {}
        self.placeholder_counter: int = 0
    
    def scrub_text(self, text: str, pii_types: Optional[List[PIIType]] = None) -> PIIResult:
        """
        Detect and redact PII while preserving placeholders.
        
        Args:
            text: Input text to scrub
            pii_types: Optional list of specific PII types to detect (default: all)
            
        Returns:
            PIIResult with scrubbed text and detection info
        """
        if not text:
            return PIIResult(
                original_text=text,
                scrubbed_text=text,
                detected_pii=[],
                placeholders={},
                is_compliant=True
            )
        
        detected_pii: List[PIIMatch] = []
        scrubbed_text = text
        pii_count_by_type: Dict[str, int] = {}
        
        # Reset placeholder tracking for this scrub operation
        self.placeholder_map = {}
        self.placeholder_counter = 0
        
        # Determine which PII types to check
        types_to_check = pii_types if pii_types else list(self.compiled_patterns.keys())
        
        # Detect and redact each PII type
        for pii_type in types_to_check:
            if pii_type not in self.compiled_patterns:
                continue
                
            pattern = self.compiled_patterns[pii_type]
            matches = list(pattern.finditer(scrubbed_text))
            
            # Process matches in reverse order to preserve positions
            for match in reversed(matches):
                original = match.group()
                placeholder = self._create_placeholder(pii_type, original)
                
                pii_match = PIIMatch(
                    pii_type=pii_type,
                    original=original,
                    placeholder=placeholder,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=self._calculate_confidence(pii_type, original)
                )
                detected_pii.append(pii_match)
                
                # Replace in text
                scrubbed_text = scrubbed_text[:match.start()] + placeholder + scrubbed_text[match.end():]
                
                # Update count
                type_name = pii_type.value
                pii_count_by_type[type_name] = pii_count_by_type.get(type_name, 0) + 1
        
        # Reverse detected_pii to maintain original order
        detected_pii.reverse()
        
        is_compliant = len(detected_pii) == 0
        
        logger.info(f"PII scrubbing complete: {len(detected_pii)} items detected, compliant={is_compliant}")
        
        return PIIResult(
            original_text=text,
            scrubbed_text=scrubbed_text,
            detected_pii=detected_pii,
            placeholders=self.placeholder_map.copy(),
            is_compliant=is_compliant,
            pii_count_by_type=pii_count_by_type
        )
    
    def _create_placeholder(self, pii_type: PIIType, original: str) -> str:
        """Create a placeholder for detected PII."""
        self.placeholder_counter += 1
        placeholder = f"[{pii_type.value.upper()}_{self.placeholder_counter}]"
        self.placeholder_map[placeholder] = original
        return placeholder
    
    def _calculate_confidence(self, pii_type: PIIType, value: str) -> float:
        """Calculate confidence score for PII detection."""
        # High confidence for well-structured patterns
        if pii_type in [PIIType.EMAIL, PIIType.SSN, PIIType.CREDIT_CARD]:
            return 0.95
        elif pii_type in [PIIType.PHONE, PIIType.IP_ADDRESS]:
            return 0.90
        elif pii_type == PIIType.URL:
            return 0.85
        else:
            return 0.80
    
    def restore_placeholders(self, scrubbed_text: str) -> str:
        """
        Restore original values from placeholders.
        
        Args:
            scrubbed_text: Text with placeholders
            
        Returns:
            Text with original PII values restored
        """
        text = scrubbed_text
        for placeholder, original in self.placeholder_map.items():
            text = text.replace(placeholder, original)
        return text
    
    def get_pii_summary(self, result: PIIResult) -> Dict[str, object]:
        """Get summary of PII detection results."""
        return {
            "total_pii_found": len(result.detected_pii),
            "is_compliant": result.is_compliant,
            "pii_by_type": result.pii_count_by_type,
            "placeholder_count": len(result.placeholders),
            "high_risk_types": [
                pii_type for pii_type in [PIIType.SSN, PIIType.CREDIT_CARD]
                if pii_type.value in result.pii_count_by_type
            ]
        }
    
    def validate_compliance(self, text: str, strict: bool = False) -> bool:
        """
        Check if text is PII-compliant without modifying it.
        
        Args:
            text: Text to validate
            strict: If True, object PII detection fails compliance
            
        Returns:
            True if compliant, False otherwise
        """
        result = self.scrub_text(text)
        
        if strict:
            return result.is_compliant
        
        # Non-strict mode: only fail on high-risk PII
        high_risk_types = {PIIType.SSN, PIIType.CREDIT_CARD}
        for pii_match in result.detected_pii:
            if pii_match.pii_type in high_risk_types:
                return False
        
        return True


# Factory functions
def create_pii_scrubber(custom_patterns: Optional[Dict[str, str]] = None) -> PIIScrubber:
    """Create PII scrubber instance."""
    return PIIScrubber(custom_patterns)


def scrub_pii(text: str, pii_types: Optional[List[PIIType]] = None) -> PIIResult:
    """Convenience function to scrub PII from text."""
    scrubber = PIIScrubber()
    return scrubber.scrub_text(text, pii_types)

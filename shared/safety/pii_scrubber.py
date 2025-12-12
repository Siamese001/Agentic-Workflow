"""PII Detection and Sanitization.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Migrated from archives/engines/legacy_engines/safety_enhancements.py
"""

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of PII to detect."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    URL = "url"
    IP_ADDRESS = "ip_address"
    DOB = "dob"
    ADDRESS = "address"


@dataclass
class PIIMatch:
    """Single PII detection match."""
    pii_type: PIIType
    original: str
    placeholder: str
    position: Tuple[int, int]
    confidence: float = 1.0


@dataclass
class PIIResult:
    """PII detection and scrubbing result."""
    original_text: str
    scrubbed_text: str
    detected_pii: List[PIIMatch]
    placeholders: Dict[str, str]
    is_compliant: bool
    
    def has_pii(self) -> bool:
        """Check if any PII was detected."""
        return len(self.detected_pii) > 0
    
    def get_pii_types(self) -> List[PIIType]:
        """Get list of detected PII types."""
        return list(set(match.pii_type for match in self.detected_pii))


class PIIScrubber:
    """Personal Information Detection and Sanitization.
    
    Detects and redacts PII while preserving placeholders for context.
    Essential for enterprise compliance (GDPR/CCPA).
    """
    
    def __init__(self, enable_logging: bool = True):
        """Initialize PII scrubber.
        
        Args:
            enable_logging: Enable logging of PII detection events
        """
        self.enable_logging = enable_logging
        
        self.pii_patterns = {
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.PHONE: r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            PIIType.URL: r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
            PIIType.IP_ADDRESS: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            PIIType.DOB: r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b',
        }
        
        self.placeholder_map: Dict[str, str] = {}
        self.placeholder_counter = 0
    
    def scrub_text(self, text: str) -> PIIResult:
        """Detect and redact PII while preserving placeholders.
        
        Args:
            text: Input text to scrub
            
        Returns:
            PIIResult with scrubbed text and detection info
        """
        if not text:
            return PIIResult(
                original_text="",
                scrubbed_text="",
                detected_pii=[],
                placeholders={},
                is_compliant=True,
            )
        
        detected_pii: List[PIIMatch] = []
        scrubbed_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, scrubbed_text, re.IGNORECASE)
            
            for match in matches:
                original = match.group()
                placeholder = self._create_placeholder(pii_type, original)
                
                pii_match = PIIMatch(
                    pii_type=pii_type,
                    original=original,
                    placeholder=placeholder,
                    position=match.span(),
                )
                
                detected_pii.append(pii_match)
                scrubbed_text = scrubbed_text.replace(original, placeholder)
        
        is_compliant = len(detected_pii) == 0
        
        if self.enable_logging and detected_pii:
            logger.warning(
                "pii_detected",
                extra={
                    "pii_count": len(detected_pii),
                    "pii_types": [m.pii_type.value for m in detected_pii],
                }
            )
        
        return PIIResult(
            original_text=text,
            scrubbed_text=scrubbed_text,
            detected_pii=detected_pii,
            placeholders=self.placeholder_map,
            is_compliant=is_compliant,
        )
    
    def _create_placeholder(self, pii_type: PIIType, original: str) -> str:
        """Create a placeholder for detected PII.
        
        Args:
            pii_type: Type of PII
            original: Original PII value
            
        Returns:
            Placeholder string
        """
        self.placeholder_counter += 1
        placeholder = f"[{pii_type.value.upper()}_{self.placeholder_counter}]"
        self.placeholder_map[placeholder] = original
        return placeholder
    
    def restore_placeholders(self, scrubbed_text: str) -> str:
        """Restore original values from placeholders.
        
        Args:
            scrubbed_text: Text with placeholders
            
        Returns:
            Text with original PII restored
        """
        text = scrubbed_text
        for placeholder, original in self.placeholder_map.items():
            text = text.replace(placeholder, original)
        return text
    
    def reset(self) -> None:
        """Reset placeholder map and counter."""
        self.placeholder_map.clear()
        self.placeholder_counter = 0


def scrub_pii(text: str) -> PIIResult:
    """Convenience function to scrub PII from text.
    
    Args:
        text: Input text
        
    Returns:
        PIIResult with scrubbed text
    """
    scrubber = PIIScrubber()
    return scrubber.scrub_text(text)

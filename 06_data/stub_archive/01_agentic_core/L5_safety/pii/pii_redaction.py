"""
pii_redaction.py - PII Detection and Redaction Module

Domain: pii
Generated: 2025-12-07T12:07:54.764827
"""

from __future__ import annotations
import logging
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """A PII match."""
    type: str
    value: str
    start: int
    end: int
    confidence: float


@dataclass
class RedactionResult:
    """Result of redaction."""
    original: str
    redacted: str
    matches: List[PIIMatch] = field(default_factory=list)


class PiiRedaction:
    """PII detector and redactor for pii domain."""
    
    PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.patterns = {**self.PATTERNS, **self.config.get("patterns", {})}
        self.redaction_char = self.config.get("redaction_char", "*")
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def detect(self, text: str) -> List[PIIMatch]:
        """Detect PII in text."""
        matches = []
        
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                matches.append(PIIMatch(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                ))
        
        return matches
    
    def redact(self, text: str, types: Optional[List[str]] = None) -> RedactionResult:
        """Redact PII from text."""
        matches = self.detect(text)
        
        if types:
            matches = [m for m in matches if m.type in types]
        
        # Sort by position (reverse) to redact from end
        matches.sort(key=lambda m: m.start, reverse=True)
        
        redacted = text
        for match in matches:
            replacement = self.redaction_char * len(match.value)
            redacted = redacted[:match.start] + replacement + redacted[match.end:]
        
        return RedactionResult(original=text, redacted=redacted, matches=matches)


def detect_pii(text: str, config: Optional[Dict] = None) -> List[PIIMatch]:
    """Detect PII in text."""
    return PiiRedaction(config).detect(text)


def redact_pii(text: str, config: Optional[Dict] = None) -> RedactionResult:
    """Redact PII from text."""
    return PiiRedaction(config).redact(text)

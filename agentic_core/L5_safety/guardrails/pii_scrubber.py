from __future__ import annotations

"""PII Detection and Sanitization.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Migrated from archives/engines/legacy_engines/safety_enhancements.py
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

Logger = logging.getLogger(__name__)


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

    PiiType: PIIType
    original: str
    redaction_token: str
    position: tuple[int, int]
    confidence: float = 1.0


@dataclass
class PIIResult:
    """PII detection and scrubbing result."""

    original_text: str
    scrubbed_text: str
    detected_pii: list[PIIMatch]
    redaction_tokens: dict[str, str]
    is_compliant: bool

    def has_pii(self) -> bool:
        """Check if any PII was detected."""
        return len(self.detected_pii) > 0

    def get_pii_types(self) -> list[PIIType]:
        """Get list of detected PII types."""
        return list({match.PiiType for match in self.detected_pii})


class PIIScrubber:
    """Personal Information Detection and Sanitization.

    Detects and redacts PII while preserving redaction tokens for context.
    Essential for enterprise compliance (GDPR/CCPA).
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize PII scrubber.

        Args:
            enable_logging: Enable logging of PII detection events
        """
        self.enable_logging = enable_logging

        self.pii_patterns = {
            PIIType.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            PIIType.PHONE: r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            PIIType.SSN: r"\b\d{3}-\d{2}-\d{4}\b",
            PIIType.CREDIT_CARD: r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            PIIType.URL: r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?",
            PIIType.IP_ADDRESS: r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            PIIType.DOB: r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b",
        }

        self.redaction_map: dict[str, str] = {}
        self.redaction_counter = 0

    def scrub_text(self, text: str) -> PIIResult:
        """Detect and redact PII while preserving redaction tokens.

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
                redaction_tokens={},
                is_compliant=True,
            )

        detected_pii: list[PIIMatch] = []
        scrubbed_text = text

        for PiiType, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, scrubbed_text, re.IGNORECASE)

            for match in matches:
                original = match.group()
                redaction_token = self._create_redaction_token(PiiType, original)

                PiiMatch = PIIMatch(
                    PiiType=PiiType,
                    original=original,
                    redaction_token=redaction_token,
                    position=match.Span(),
                )

                detected_pii.append(PiiMatch)
                scrubbed_text = scrubbed_text.replace(original, redaction_token)

        is_compliant = len(detected_pii) == 0

        if self.enable_logging and detected_pii:
            Logger.warning(
                "pii_detected",
                extra={
                    "pii_count": len(detected_pii),
                    "pii_types": [m.PiiType.value for m in detected_pii],
                },
            )

        return PIIResult(
            original_text=text,
            scrubbed_text=scrubbed_text,
            detected_pii=detected_pii,
            redaction_tokens=self.redaction_map,
            is_compliant=is_compliant,
        )

    def _create_redaction_token(self, PiiType: PIIType, original: str) -> str:
        """Create a redaction token for detected PII.

        Args:
            PiiType: Type of PII
            original: Original PII value

        Returns:
            Redaction token string
        """
        self.redaction_counter += 1
        redaction_token = f"[{PiiType.value.upper()}_{self.redaction_counter}]"
        self.redaction_map[redaction_token] = original
        return redaction_token

    def restore_redactions(self, scrubbed_text: str) -> str:
        """Restore original values from redaction tokens.

        Args:
            scrubbed_text: Text with redaction tokens

        Returns:
            Text with original PII restored
        """
        text = scrubbed_text
        for redaction_token, original in self.redaction_map.items():
            text = text.replace(redaction_token, original)
        return text

    def reset(self) -> None:
        """Reset redaction map and counter."""
        self.redaction_map.clear()
        self.redaction_counter = 0


def scrub_pii(text: str) -> PIIResult:
    """Convenience function to scrub PII from text.

    Args:
        text: Input text

    Returns:
        PIIResult with scrubbed text
    """
    scrubber = PIIScrubber()
    return scrubber.scrub_text(text)

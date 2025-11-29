"""
PII Filter for L5 Safety Layer

Detects and filters personally identifiable information.
"""

import re
from typing import Tuple, List

class PIIFilter:
    """Filters PII from text content."""

    def __init__(self):
        # Regex patterns for PII detection
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    def filter_pii(self, text: str) -> Tuple[str, List[str]]:
        """Filter PII from text and return (filtered_text, detected_types)."""
        detected_types = []
        filtered_text = text

        if self.email_pattern.search(text):
            detected_types.append("email")
            filtered_text = self.email_pattern.sub("[EMAIL]", filtered_text)

        if self.phone_pattern.search(text):
            detected_types.append("phone")
            filtered_text = self.phone_pattern.sub("[PHONE]", filtered_text)

        if self.ssn_pattern.search(text):
            detected_types.append("ssn")
            filtered_text = self.ssn_pattern.sub("[SSN]", filtered_text)

        return filtered_text, detected_types

"""
Safety Validator for L5 Safety Layer

Validates content against safety rules and policies.
"""

from typing import Dict, Any

class SafetyValidator:
    """Validates content for safety compliance."""

    def __init__(self):
        self.validation_rules = {
            "pii_detection": True,
            "content_filtering": True,
            "policy_compliance": True
        }

    def validate(self, content: str) -> Dict[str, Any]:
        """Validate content against all safety rules."""
        results = {
            "is_safe": True,
            "violations": [],
            "warnings": [],
            "score": 1.0
        }

        # Check for PII
        if self._contains_pii(content):
            results["violations"].append("pii_detected")
            results["is_safe"] = False
            results["score"] -= 0.3

        # Check for unsafe content
        if self._contains_unsafe_content(content):
            results["violations"].append("unsafe_content")
            results["is_safe"] = False
            results["score"] -= 0.4

        # Check length limits
        if self._exceeds_length_limit(content):
            results["warnings"].append("content_too_long")
            results["score"] -= 0.1

        results["score"] = max(0.0, results["score"])
        return results

    def _contains_pii(self, content: str) -> bool:
        """Check if content contains PII."""
        import re
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b\d{3}-\d{3}-\d{4}\b')
        return bool(email_pattern.search(content) or phone_pattern.search(content))

    def _contains_unsafe_content(self, content: str) -> bool:
        """Check if content contains unsafe material."""
        unsafe_keywords = ["password", "secret", "token", "key"]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in unsafe_keywords)

    def _exceeds_length_limit(self, content: str) -> bool:
        """Check if content exceeds length limits."""
        return len(content) > 10000

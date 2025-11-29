"""
Content Filter for L5 Safety Layer

Filters and validates content for safety compliance.
"""

from typing import Tuple, List

class ContentFilter:
    """Filters content for safety violations."""

    def __init__(self):
        # Basic safety keywords
        self.unsafe_keywords = [
            "password", "secret", "token", "key", "credential",
            "private", "confidential", "internal_only"
        ]

    def filter_content(self, text: str) -> Tuple[str, List[str]]:
        """Filter unsafe content and return (filtered_text, violations)."""
        violations = []
        filtered_text = text.lower()

        for keyword in self.unsafe_keywords:
            if keyword in filtered_text:
                violations.append(keyword)
                filtered_text = filtered_text.replace(keyword, f"[FILTERED:{keyword}]")

        return filtered_text, violations

    def is_safe(self, text: str) -> bool:
        """Check if content is safe."""
        _, violations = self.filter_content(text)
        return len(violations) == 0

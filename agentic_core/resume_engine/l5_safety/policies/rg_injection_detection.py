# Injection detection system
from typing import List, Optional
from dataclasses import dataclass

from .types import SafetyContext, Verdict

@dataclass
class InjectionDetector:
    """Detects various types of injection attacks"""
    enabled: bool = True
    patterns: List[str] = None

    def __post_init__(self):
        if self.patterns is None:
            self.patterns = [
                "DROP TABLE",
                "UNION SELECT",
                "script>",
                "javascript:",
                "eval(",
                "exec(",
                "$(",
                "#{",
                "%{",
                "{{"
            ]

    def detect(self, input_text: str, context: Optional[SafetyContext] = None) -> Verdict:
        """Detect injection patterns in input text"""
        if not self.enabled:
            return Verdict.SAFE

        if not input_text:
            return Verdict.SAFE

        text_lower = input_text.lower()
        for pattern in self.patterns:
            if pattern.lower() in text_lower:
                return Verdict.VIOLATION

        return Verdict.SAFE

def create_injection_safety_policy() -> InjectionDetector:
    """Create a default injection safety policy"""
    return InjectionDetector()

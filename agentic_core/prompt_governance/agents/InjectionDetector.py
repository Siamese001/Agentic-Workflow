# Prompt Injection Heuristics
# Strategy: Keyword blocking (heuristic) for speed. Phase 5 adds model-based checks.

from typing import List
from agentic_core.domain.exceptions import SecurityViolationError

class InjectionDetector:
    """
    Scans text for adversarial patterns.
    """
    
    # Common jailbreak phrases (lowercase for normalization)
    BLOCKLIST = [
        "ignore previous instructions",
        "ignore all prior instructions",
        "system override",
        "dan mode",
        "developer mode on",
        "act as an unrestricted"
    ]

    def scan(self, text: str) -> bool:
        """
        Checks for injection patterns.
        Raises SecurityViolationError if found.
        Returns True if safe.
        """
        if not text:
            return True
            
        normalized = text.lower()
        
        for phrase in self.BLOCKLIST:
            if phrase in normalized:
                raise SecurityViolationError(
                    message=f"Detected potential prompt injection: '{phrase}'",
                    violation_type="PROMPT_INJECTION"
                )
        
        return True

"""
L5 — Injection Detector

Responsibilities:
    • Detect prompt injection or malicious input patterns before execution.
    • Provide signals to the safety gateway and policy engine for enforcement.
    • Operate independently from orchestration flow while integrating with monitoring.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Dict, List

from utils_types import StatePatch


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    KNOWN_PATTERNS: List[str] = [
        "ignore previous instructions",
        "override system",
        "disable safety",
        "run arbitrary code",
    ]

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        lower_content = content.lower()
        for pattern in self.KNOWN_PATTERNS:
            if pattern in lower_content:
                matches.append(pattern)

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                }
            }
        )
        return patch

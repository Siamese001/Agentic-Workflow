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

from prompt_taxonomy import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from safety_config import InjectionPattern, SafetyConfig, load_default_safety_config
from utils_types import StatePatch


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()
        self.patterns: List[str] = DEFAULT_INJECTION_PATTERNS
        self.instructional_types: List[str] = INSTRUCTIONAL_INJECTION_ALL

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        matched_patterns: List[str] = []
        lower_content = content.lower()
        for pattern in self.patterns:
            normalized_pattern = pattern.replace("_", " ")
            if pattern in lower_content or normalized_pattern in lower_content:
                matches.append(pattern)
                matched_patterns.append(pattern)

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                    "matched_patterns": matched_patterns,
                    "instructional_types": self.instructional_types,
                }
            }
        )
        return patch

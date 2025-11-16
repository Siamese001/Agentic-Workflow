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

from safety_config import InjectionPattern, SafetyConfig, load_default_safety_config
from utils_types import StatePatch


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()
        default_patterns = load_default_safety_config().injection_patterns
        self.patterns: List[InjectionPattern] = self._config.injection_patterns or default_patterns

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        matched_patterns: List[InjectionPattern] = []
        lower_content = content.lower()
        for pattern in self.patterns:
            if not pattern.enabled:
                continue
            if pattern.pattern in lower_content:
                matches.append(pattern.pattern)
                matched_patterns.append(pattern)

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                    "matched_patterns": [matched_pattern.pattern for matched_pattern in matched_patterns],
                }
            }
        )
        return patch

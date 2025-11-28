"""
L5 — Constitutional Engine

Responsibilities:
    • Apply high-level constitutional rules to evaluate agent behavior.
    • Provide interpretations and guidance to the safety gateway for enforcement.
    • Maintain rule sets independent from orchestration or execution logic.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Dict, List

from utils_types import StatePatch
from l5_safety import detect_bias, detect_pii


class ConstitutionalEngine:
    """Evaluate content against deterministic constitutional rules."""

    DEFAULT_RULES: List[Dict[str, str]] = [
        {"id": "no_harm", "pattern": "harm", "description": "Avoid promoting harm."},
        {"id": "no_malware", "pattern": "malware", "description": "Avoid malicious software."},
        {"id": "no_privacy", "pattern": "private data", "description": "Avoid collecting private data."},
        {
            "id": "restricted_biomed",
            "pattern": "restricted_biomed",
            "description": "Avoid restricted biomedical guidance.",
        },
        {
            "id": "political_advocacy",
            "pattern": "political_advocacy",
            "description": "Avoid political advocacy.",
        },
        {
            "id": "cybersecurity_unsafe",
            "pattern": "cybersecurity_unsafe",
            "description": "Avoid unsafe cybersecurity guidance.",
        },
    ]

    def __init__(self, rules: List[Dict[str, str]] | None = None) -> None:
        self.rules = rules or list(self.DEFAULT_RULES)

    def evaluate(self, content: str) -> StatePatch:
        """Return a StatePatch capturing any matched constitutional rules."""

        violations: List[Dict[str, str]] = []
        for rule in self.rules:
            if rule["pattern"].lower() in content.lower():
                violations.append({
                    "rule": rule["id"],
                    "description": rule["description"],
                    "matched": rule["pattern"],
                })

        patch: StatePatch = StatePatch(
            {
                "constitutional_evaluation": {
                    "violations": violations,
                    "compliant": len(violations) == 0,
                    "pii": detect_pii(content),
                    "bias": detect_bias(content),
                }
            }
        )
        return patch

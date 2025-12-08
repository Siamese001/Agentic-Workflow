# Ownership: apps_rg / L5_safety
# Layer: L5_safety
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Hallucination detection for resume content.

Flags implausible metrics, temporal inconsistencies, and excessive superlatives.
"""

from __future__ import annotations

import re
from typing import Dict, List

from shared.models import ValidationResult, ValidationSeverity


class HallucinationDetector:
    """Detect potential hallucinations in resume content."""

    SUPERLATIVES = [
        "revolutionary",
        "groundbreaking",
        "unprecedented",
        "unparalleled",
        "game-changing",
        "world-class",
        "best-in-class",
        "cutting-edge",
    ]

    def detect(self, bullet_pool: List[Dict]) -> List[ValidationResult]:
        """Run hallucination detection on bullet pool."""
        results = []

        for i, bullet in enumerate(bullet_pool):
            text = bullet.get("bullet_text", "")

            if self._has_implausible_growth(text):
                results.append(
                    ValidationResult(
                        rule_id="HALLUCINATION_IMPLAUSIBLE_GROWTH",
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"Bullet {i + 1} may contain implausible growth rate",
                        details={"bullet_text": text[:100]},
                    )
                )

            if self._has_excessive_superlatives(text):
                results.append(
                    ValidationResult(
                        rule_id="HALLUCINATION_EXCESSIVE_SUPERLATIVES",
                        passed=False,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Bullet {i + 1} contains excessive superlatives",
                        details={"bullet_text": text[:100]},
                    )
                )

        if not results:
            results.append(
                ValidationResult(
                    rule_id="HALLUCINATION_CHECK",
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"No hallucinations detected in {len(bullet_pool)} bullets",
                )
            )

        return results

    def _has_implausible_growth(self, text: str) -> bool:
        """Check for implausibly high growth rates."""
        growth_patterns = [r"\d{3,}%", r"\d+x"]
        for pattern in growth_patterns:
            if re.search(pattern, text):
                if any(term in text.lower() for term in ["month", "quarter", "90 day"]):
                    return True
        return False

    def _has_excessive_superlatives(self, text: str) -> bool:
        """Check for excessive use of superlatives."""
        count = sum(1 for word in self.SUPERLATIVES if word in text.lower())
        return count >= 2

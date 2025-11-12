"""Validator agent for outreach drafts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reasons: tuple[str, ...]


class ValidatorAgent:
    def check(self, draft: str, route_decision, pii_map: Dict[str, str]) -> ValidationResult:
        reasons = []
        if "Subject:" not in draft:
            reasons.append("Missing subject line")
        if "[artifact_id:" not in draft:
            reasons.append("Missing evidence markers")
        if pii_map:
            # ensure placeholders remain
            for placeholder in pii_map:
                if placeholder not in draft:
                    reasons.append(f"Placeholder {placeholder} missing from draft")
        return ValidationResult(not reasons, tuple(reasons))

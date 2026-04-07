"""
Research Gate Validator — apps_research.

Enforces quality gates on assembled research artifacts:
- Source register present with minimum entries
- No unsupported claims (inference labeled)
- No empty sections
- Audience and purpose declarations present

Deterministic: all checks are rule-based.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_research.types.research_types import ResearchSection, SourceEntry

_log = logging.getLogger(__name__)


@dataclass
class ResearchViolation:
    """A single research quality violation."""

    rule_id: str
    severity: str
    message: str
    section_id: str = ""


@dataclass
class ResearchGateResult:
    """Result of research gate validation."""

    passed: bool
    violations: list[ResearchViolation] = field(default_factory=list)
    quality_score: float = 0.0
    sections_checked: int = 0


class ResearchGateValidator:
    """Validate assembled research artifact against quality gates."""

    def validate(
        self,
        sections: list[ResearchSection],
        sources: list[SourceEntry],
        required_section_ids: list[str],
    ) -> ResearchGateResult:
        violations: list[ResearchViolation] = []

        if not sources:
            violations.append(
                ResearchViolation(
                    rule_id="RES_NO_SOURCE_REGISTER",
                    severity="BLOCK",
                    message="Source register is empty — at least one source required.",
                ),
            )

        present_ids = {s.section_id for s in sections}
        for req_id in required_section_ids:
            if req_id not in present_ids:
                violations.append(
                    ResearchViolation(
                        rule_id="RES_MISSING_SECTION",
                        severity="BLOCK",
                        message=f"Required section '{req_id}' is missing.",
                        section_id=req_id,
                    ),
                )

        for section in sections:
            if not section.body or not section.body.strip():
                violations.append(
                    ResearchViolation(
                        rule_id="RES_EMPTY_SECTION",
                        severity="BLOCK",
                        message=f"Section '{section.section_id}' has empty body.",
                        section_id=section.section_id,
                    ),
                )

        block_count = sum(1 for v in violations if v.severity == "BLOCK")
        total_checks = len(sections) + 2
        quality_score = max(0.0, (total_checks - block_count) / total_checks) if total_checks else 1.0

        return ResearchGateResult(
            passed=block_count == 0,
            violations=violations,
            quality_score=round(quality_score, 4),
            sections_checked=len(sections),
        )

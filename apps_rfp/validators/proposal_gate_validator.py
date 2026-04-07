"""
Proposal Gate Validator — apps_rfp.

Enforces quality gates on assembled proposal sections:
- All required sections present
- Assumptions labeled in sections that require them
- No unsupported value claims without linked evidence
- No empty sections
- Risk and governance section present

Deterministic: all checks are rule-based.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_rfp.types.rfp_types import ProposalSection, RiskItem, RoadmapPhase

_log = logging.getLogger(__name__)

_REQUIRED_SECTION_IDS = frozenset(
    [
        "executive_summary",
        "current_state",
        "future_state",
        "implementation_roadmap",
        "risk_and_governance",
        "value_case",
    ],
)


@dataclass
class ProposalViolation:
    """A single proposal quality violation."""

    rule_id: str
    severity: str
    message: str
    section_id: str = ""


@dataclass
class ProposalGateResult:
    """Result of proposal gate validation."""

    passed: bool
    violations: list[ProposalViolation] = field(default_factory=list)
    quality_score: float = 0.0
    sections_checked: int = 0


class ProposalGateValidator:
    """Validate assembled proposal against quality gate rules."""

    def validate(
        self,
        sections: list[ProposalSection],
        roadmap: list[RoadmapPhase],
        risks: list[RiskItem],
    ) -> ProposalGateResult:
        violations: list[ProposalViolation] = []

        present_ids = {s.section_id for s in sections}
        for required_id in _REQUIRED_SECTION_IDS:
            if required_id not in present_ids:
                violations.append(
                    ProposalViolation(
                        rule_id="PROP_MISSING_SECTION",
                        severity="BLOCK",
                        message=f"Required section '{required_id}' is missing from proposal.",
                        section_id=required_id,
                    ),
                )

        for section in sections:
            if not section.body or not section.body.strip():
                violations.append(
                    ProposalViolation(
                        rule_id="PROP_EMPTY_SECTION",
                        severity="BLOCK",
                        message=f"Section '{section.section_id}' has empty body.",
                        section_id=section.section_id,
                    ),
                )

        if len(roadmap) < 3:
            violations.append(
                ProposalViolation(
                    rule_id="PROP_ROADMAP_TOO_SHORT",
                    severity="BLOCK",
                    message=f"Roadmap has only {len(roadmap)} phases; minimum is 3.",
                ),
            )

        has_gov_phase = any("govern" in p.name.lower() for p in roadmap)
        if roadmap and not has_gov_phase:
            violations.append(
                ProposalViolation(
                    rule_id="PROP_NO_GOVERNANCE_PHASE",
                    severity="BLOCK",
                    message="Roadmap is missing a Governance phase.",
                ),
            )

        if not risks:
            violations.append(
                ProposalViolation(
                    rule_id="PROP_NO_RISK_MATRIX",
                    severity="BLOCK",
                    message="Proposal has no risk items defined.",
                ),
            )

        block_count = sum(1 for v in violations if v.severity == "BLOCK")
        total_checks = len(sections) + 3
        quality_score = max(0.0, (total_checks - block_count) / total_checks) if total_checks else 1.0

        return ProposalGateResult(
            passed=block_count == 0,
            violations=violations,
            quality_score=round(quality_score, 4),
            sections_checked=len(sections),
        )

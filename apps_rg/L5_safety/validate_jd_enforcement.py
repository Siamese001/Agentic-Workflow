# Ownership: apps_rg / L5_safety
# Layer: L5_safety
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Job Description enforcement validation.

Ensures JD is always used and never mocked throughout the workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class JDEnforcementRule(Enum):
    """Enforcement rules ensuring JD is always used."""

    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    E3_JD_PARSING_SUCCESS = "JD must parse successfully"
    E4_THEMES_EXTRACTED = "JD-derived themes must be extracted"
    E5_SKILLS_EXTRACTED = "JD-derived skills must be extracted (min 5)"
    E6_JD_TO_THEMATIC = "JD data must flow to ThematicAnalysis"
    E7_THEMATIC_USES_JD = "ThematicAnalysis must use JD data (not mock)"
    E8_ARTIST_RECEIVES_JD = "Artist must receive JD-derived thematic_analysis"
    E9_CONTENT_HAS_JD_KW = "Generated content must contain JD keywords"
    E10_ENRICHMENT_USES_JD = "Enrichment must use JD-derived data"
    E11_VALIDATION_CHECKS_JD = "Validation must check JD keyword presence"
    E12_FILES_CONTAIN_JD = "Output files must contain JD-derived content"
    E13_QA_VERIFIES_JD = "QA report must verify JD usage"
    E14_NO_MOCK_DATA = "No fallback/mock/default data allowed anywhere"
    E15_COMPLETE_AUDIT = "Complete audit trail of JD data flow required"


@dataclass
class JDEnforcementResult:
    """Result of a JD enforcement check."""

    rule: JDEnforcementRule
    passed: bool
    details: str
    gate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JDEnforcementValidator:
    """Validator ensuring JD is always used and never mocked."""

    def __init__(self) -> None:
        """Initialize the JD enforcement validator."""
        self.enforcement_results: List[JDEnforcementResult] = []
        self.jd_hash: Optional[str] = None
        self.jd_keywords: List[str] = []

    def validate_jd_input(
        self, job_description: str, gate_id: str
    ) -> List[JDEnforcementResult]:
        """Validate JD input at GATE-0."""
        results = []

        # E1: Min length
        passed = len(job_description) >= 100
        results.append(
            JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                passed,
                f"JD length: {len(job_description)} chars",
                gate_id,
            )
        )

        # E2: Non-null
        passed = bool(job_description and job_description.strip())
        results.append(
            JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                passed,
                "JD is non-empty" if passed else "JD is empty or None",
                gate_id,
            )
        )

        self.enforcement_results.extend(results)
        return results

    def get_all_results(self) -> List[JDEnforcementResult]:
        """Get all enforcement results."""
        return self.enforcement_results

    def has_failures(self) -> bool:
        """Check if any enforcement checks failed."""
        return any(not r.passed for r in self.enforcement_results)

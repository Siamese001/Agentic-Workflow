# Ownership: apps_rg / L2_execution
# Layer: L2_execution
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Data enrichment for resume generation HOP-2.

Enriches bullet pool with canonical verbs and deduplication.
"""

import logging
from typing import Dict, List, Optional, Tuple


class DataEnricher:
    """HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc."""

    def __init__(self) -> None:
        """Initialize the data enricher."""
        self.verb_canonicalizer = VerbCanonicalizer()
        self.duplicate_detector = DuplicateDetector()

    def enrich(
        self,
        extracted_data: Dict,
        thematic_analysis: Optional[Dict] = None,
        orchestrator: Optional[object] = None,
    ) -> Tuple[Dict, List[ValidationResult]]:
        """Enrich extracted data with additional metadata."""
        validation_results: List[ValidationResult] = []

        if orchestrator is not None:
            orchestrator.dup_detector = self.duplicate_detector

        experience_sections = extracted_data.get("experience_sections", [])
        all_bullets = []

        for section in experience_sections:
            for bullet in section.get("bullets", []):
                bullet_text = bullet.get("bullet_text", "")
                bullet["canonical_verbs"] = self.verb_canonicalizer.canonicalize(bullet_text)

                forbidden = self.verb_canonicalizer.check_for_forbidden_verbs(bullet_text)
                if forbidden:
                    validation_results.append(
                        ValidationResult(
                            rule_id="FORBIDDEN_VERB_USAGE",
                            PASSED=False,
                            SEVERITY=ValidationSeverity.MEDIUM,
                            MESSAGE=f"Forbidden verb(s): {', '.join(forbidden)}",
                            DETAILS={"bullet_text": bullet_text[:100]},
                        )
                    )
                all_bullets.append(bullet)

        duplicates = self.duplicate_detector.find_duplicates(all_bullets)
        if duplicates:
            validation_results.append(
                ValidationResult(
                    rule_id="DUPLICATE_BULLETS",
                    PASSED=False,
                    SEVERITY=ValidationSeverity.MEDIUM,
                    MESSAGE=f"Found {len(duplicates)} potential duplicate bullets",
                    DETAILS={"duplicates": duplicates[:5]},
                )
            )
        else:
            validation_results.append(
                ValidationResult(
                    rule_id="DUPLICATE_CHECK",
                    PASSED=True,
                    SEVERITY=ValidationSeverity.INFO,
                    MESSAGE="No duplicate bullets detected",
                )
            )

        return {**extracted_data, "experience_sections": experience_sections}, validation_results
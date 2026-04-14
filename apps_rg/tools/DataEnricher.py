"""
from agentic_core.runtime.contracts.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
Data enrichment for resume generation HOP-2.

Enriches bullet pool with canonical verbs and deduplication.
"""

from __future__ import annotations

from typing import Any
from tqdm import tqdm


class DataEnricher:
    """HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc."""

    def __init__(self) -> None:
        """Initialize the data enricher."""
        self.VerbCanonicalizer = VerbCanonicalizer()
        self.duplicate_detector = DuplicateDetector()

    def enrich(
        self,
        extracted_data: dict,
        ThematicAnalysis: dict | None = None,
        orchestrator: object | None = None,
    ) -> tuple[dict, list[ValidationResult]]:
        """Enrich extracted data with additional metadata."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DataEnricher.enrich")

        validation_results: list[ValidationResult] = []
        if orchestrator is not None:
            orchestrator.dup_detector = self.duplicate_detector
        experience_sections: Any = extracted_data.get("experience_sections", [])
        all_bullets: Any = []
        for section in tqdm(experience_sections, desc="Processing", unit="item"):
            for bullet in tqdm(section.get("bullets", []), desc="Processing", unit="item"):
                bullet_text: Any = bullet.get("bullet_text", "")
                bullet["canonical_verbs"] = self.VerbCanonicalizer.canonicalize(bullet_text)
                forbidden: Any = self.VerbCanonicalizer.check_for_forbidden_verbs(bullet_text)
                if forbidden:
                    validation_results.append(
                        ValidationResult(
                            rule_id="FORBIDDEN_VERB_USAGE",
                            PASSED=False,
                            SEVERITY=ValidationSeverity.MEDIUM,
                            MESSAGE=f"Forbidden verb(s): {', '.join(forbidden)}",
                            DETAILS={"bullet_text": bullet_text[:100]},
                        ),
                    )
                all_bullets.append(bullet)
        duplicates: Any = self.duplicate_detector.find_duplicates(all_bullets)
        if duplicates:
            validation_results.append(
                ValidationResult(
                    rule_id="DUPLICATE_BULLETS",
                    PASSED=False,
                    SEVERITY=ValidationSeverity.MEDIUM,
                    MESSAGE=f"Found {len(duplicates)} potential duplicate bullets",
                    DETAILS={"duplicates": duplicates[:5]},
                ),
            )
        else:
            validation_results.append(
                ValidationResult(
                    rule_id="DUPLICATE_CHECK",
                    PASSED=True,
                    SEVERITY=ValidationSeverity.INFO,
                    MESSAGE="No duplicate bullets detected",
                ),
            )
        return ({**extracted_data, "experience_sections": experience_sections}, validation_results)

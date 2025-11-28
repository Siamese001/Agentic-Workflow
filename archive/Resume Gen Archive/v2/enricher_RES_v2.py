# File: enricher_RES_v2.py
# DataEnricher class - enriches extracted data with metadata

import logging
from typing import Dict, List, Tuple

from models_RES import ValidationResult, ValidationSeverity, ThematicAnalysis
# --- REFACTOR: Import global CONFIG ---
from config_RES_v2 import CONFIG
# --- END REFACTOR ---
from utils_RES_v2 import DuplicateDetector

logger = logging.getLogger(__name__)


class DataEnricher:

    # --- REFACTOR: Remove config injection, use global CONFIG ---
    def __init__(self):
        self.duplicate_detector = DuplicateDetector()
        
        # --- BUG 2 FIX: Access canonical_verbs from CONFIG.enricher ---
        if not hasattr(CONFIG, 'enricher') or not hasattr(CONFIG.enricher, 'canonical_verbs'):
            logger.critical("FATAL: CONFIG.enricher.canonical_verbs not found. Enricher will fail.")
            raise AttributeError("CONFIG.enricher.canonical_verbs is not loaded. Check config_RES_v2.py.")
        
        self.CANONICAL_VERBS = CONFIG.enricher.canonical_verbs
    # --- END REFACTOR ---

    def _canonicalize_verbs(self, text: str) -> List[str]:
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(
        self,
        extracted_data: Dict,
        thematic_analysis: ThematicAnalysis,
        orchestrator=None
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        Returns: (enriched_data, validation_results)
        """
        validation_results = []

        experience_sections = extracted_data.get("experience_sections", [])

        all_bullets = []
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                canonical_verbs = self._canonicalize_verbs(bullet.get("bullet_text", ""))
                bullet["canonical_verbs"] = canonical_verbs

                all_bullets.append(bullet)

        # Check for duplicate bullets across all sections
        all_bullet_texts = [b.get("bullet_text", "") for b in all_bullets]
        duplicates = self.duplicate_detector.find_duplicates_in_list(all_bullet_texts)
        
        if duplicates:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_BULLETS",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Found {len(duplicates)} potential duplicate bullets",
                details={"duplicates": duplicates[:5]}
            ))
        else:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_CHECK",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="No duplicate bullets detected"
            ))

        enriched_data = {
            **extracted_data,
            "experience_sections": experience_sections
        }

        return enriched_data, validation_results

# File: enricher_RES_v3_8.py
# DataEnricher class - enriches extracted data with metadata
# Version: 3.8.0 - Complete V3.8 Migration

import logging
from typing import Dict, List, Tuple

from models_RES import ValidationResult, ValidationSeverity, ThematicAnalysis
# Import global CONFIG from v3.8
from config_RES_v3_8 import CONFIG
from utils_RES_v3_8 import DuplicateDetector

logger = logging.getLogger(__name__)


class DataEnricher:
    """
    Data enrichment service that adds metadata and semantic analysis to extracted data.
    V3.8 version with corrected imports and configuration access.
    """

    def __init__(self):
        self.duplicate_detector = DuplicateDetector()
        
        # Access canonical_verbs from CONFIG.enricher
        if not hasattr(CONFIG, 'enricher') or not hasattr(CONFIG.enricher, 'canonical_verbs'):
            logger.critical("FATAL: CONFIG.enricher.canonical_verbs not found. Enricher will fail.")
            raise AttributeError("CONFIG.enricher.canonical_verbs is not loaded. Check config_RES_v3_8.py.")
        
        self.CANONICAL_VERBS = CONFIG.enricher.canonical_verbs

    def _canonicalize_verbs(self, text: str) -> List[str]:
        """
        Find canonical forms of action verbs in text.
        
        Args:
            text: Text to analyze for verbs
            
        Returns:
            List of canonical verb forms found
        """
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(
        self,
        extracted_data: Dict,
        thematic_analysis: ThematicAnalysis,
        master_resume: Dict = None
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        
        Args:
            extracted_data: Data extracted by ClerkExtractor
            thematic_analysis: Theme analysis from JD analyzer
            master_resume: Optional master resume for additional context
            
        Returns:
            Tuple of (enriched_data, validation_results)
        """
        validation_results = []

        # Process experience sections
        experience_sections = extracted_data.get("experience_sections", [])

        all_bullets = []
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                # Add canonical verb metadata
                canonical_verbs = self._canonicalize_verbs(bullet.get("bullet_text", ""))
                bullet["canonical_verbs"] = canonical_verbs
                
                # Add theme relevance scoring placeholder
                bullet["theme_relevance"] = 0.0
                
                # Add keyword density metadata
                bullet["keyword_density"] = 0.0
                
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

        # Add thematic metadata
        if thematic_analysis and thematic_analysis.primary_theme:
            primary_theme_name = thematic_analysis.primary_theme.get("name", "")
            primary_keywords = thematic_analysis.primary_theme.get("keywords", [])
        else:
            primary_theme_name = ""
            primary_keywords = []

        # Create enriched data structure
        enriched_data = {
            **extracted_data,
            "experience_sections": experience_sections,
            "metadata": {
                "total_bullets": len(all_bullets),
                "unique_bullets": len(set(all_bullet_texts)),
                "primary_theme": primary_theme_name,
                "theme_keywords": primary_keywords,
                "enrichment_timestamp": self._get_timestamp()
            }
        }

        # Add skills enrichment if present
        if master_resume and "strategic_and_technical_competencies" in master_resume:
            skills_data = master_resume["strategic_and_technical_competencies"]
            enriched_data["skills_metadata"] = self._enrich_skills(skills_data, primary_keywords)

        return enriched_data, validation_results

    def _enrich_skills(self, skills_data: Dict, theme_keywords: List[str]) -> Dict:
        """
        Enrich skills data with theme relevance scoring.
        
        Args:
            skills_data: Raw skills data from master resume
            theme_keywords: Keywords from primary theme
            
        Returns:
            Enriched skills metadata
        """
        theme_keywords_lower = [kw.lower() for kw in theme_keywords]
        
        enriched_skills = {
            "categories": []
        }
        
        for category, skills_list in skills_data.items():
            if not isinstance(skills_list, list):
                continue
                
            # Score each skill for theme relevance
            scored_skills = []
            for skill in skills_list:
                skill_lower = skill.lower()
                relevance_score = sum(1 for kw in theme_keywords_lower if kw in skill_lower)
                scored_skills.append({
                    "skill": skill,
                    "relevance_score": relevance_score,
                    "is_theme_relevant": relevance_score > 0
                })
            
            enriched_skills["categories"].append({
                "name": category,
                "skills": scored_skills,
                "total_skills": len(scored_skills),
                "relevant_skills": sum(1 for s in scored_skills if s["is_theme_relevant"])
            })
        
        return enriched_skills

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# Backwards compatibility alias
EnrichmentService = DataEnricher

__all__ = ['DataEnricher', 'EnrichmentService']

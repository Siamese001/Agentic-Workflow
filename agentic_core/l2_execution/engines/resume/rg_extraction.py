#!/usr/bin/env python3
"""
Resume Engine Extraction Layer (L2)
Core extraction and enrichment capabilities for resume generation
"""

import re
from typing import Dict, List, Tuple, Any, Optional

from ..utils.rg_models import (
    ValidationResult, 
    BulletProvenance
)
from ..config.rg_constants import CANONICAL_VERBS


class ClerkExtractor:
    """Master resume extraction component that structures raw resume data"""

    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self._validate_master_resume_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        """Extract structured data from master resume"""
        validation_results = []

        experience_sections = self._build_experience_sections()

        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([bullet['bullet_text'] for bullet in section.get('bullets', [])])

        bullet_dicts = [{'bullet_text': b} for b in all_bullets]

        extracted_data = {
            "experience_sections": experience_sections,
            "header": self.master_resume.get("header", {}),
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications_and_credentials", []),
            "strategic_and_technical_competencies": self.master_resume.get("strategic_and_technical_competencies", [])
        }

        return extracted_data, validation_results

    def _validate_master_resume_structure(self):
        """Validate master resume has required structure"""
        required_keys = ["owner", "professional_experience", "education", "certifications_and_credentials", "strategic_and_technical_competencies"]
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")

        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            raise ValueError(f"MASTER_RESUME_JSON is missing required keys: {', '.join(missing_keys)}")
        print("  ✓ Master resume structure validated.")

    def _build_experience_sections(self) -> List[Dict]:
        """Build structured experience sections from master resume"""
        experience_sections = []

        for exp in self.master_resume.get("professional_experience", []):
            bullets = []
            bullet_source = exp.get("bullet_pool", exp.get("highlights", []))

            for bullet_text in bullet_source:
                bullets.append({
                    "bullet_text": bullet_text,
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.VERBATIM.value
                })

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""),
                "end_date": exp.get("dates", {}).get("end", ""),
                "overview": exp.get("overview", ""),
                "bullets": bullets,
                "highlights": [bullet['bullet_text'] for bullet in bullets]
            })

        return experience_sections


class DuplicateDetector:
    """Duplicate bullet point detector using TF-IDF cosine similarity"""

    def __init__(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            self.vectorizer = TfidfVectorizer(stop_words='english', norm='l2')
            self.cosine_similarity = cosine_similarity
            self.sklearn_available = True
        except ImportError:
            self.sklearn_available = False
            print("Warning: sklearn not available, using fallback duplicate detection")

    def find_duplicates(
        self,
        bullets: List[Dict],
        threshold: float = 0.9
    ) -> List[Tuple[int, int, float]]:
        """
        Find bullets with cosine similarity >= threshold.
        Returns: List of (index1, index2, similarity_score)
        """
        duplicates = []

        if len(bullets) < 2:
            return duplicates

        # Extract bullet texts
        texts = [bullet.get("bullet_text", "") for bullet in bullets]
        
        # Filter out empty texts
        valid_indices = [i for i, text in enumerate(texts) if text.strip()]
        valid_texts = [texts[i] for i in valid_indices]
        
        if len(valid_texts) < 2:
            return duplicates

        if self.sklearn_available:
            try:
                # Calculate TF-IDF vectors
                tfidf_matrix = self.vectorizer.fit_transform(valid_texts)
                
                # Calculate cosine similarity matrix
                similarity_matrix = self.cosine_similarity(tfidf_matrix)
                
                # Find duplicates above threshold
                for i in range(len(valid_texts)):
                    for j in range(i + 1, len(valid_texts)):
                        similarity = similarity_matrix[i][j]
                        if similarity >= threshold:
                            # Map back to original indices
                            original_i = valid_indices[i]
                            original_j = valid_indices[j]
                            duplicates.append((original_i, original_j, float(similarity)))
                            
            except Exception as e:
                # Fallback to simpler similarity calculation if TF-IDF fails
                return self._fallback_duplicate_detection(bullets, threshold)
        else:
            return self._fallback_duplicate_detection(bullets, threshold)

        return duplicates

    def _fallback_duplicate_detection(
        self, 
        bullets: List[Dict], 
        threshold: float
    ) -> List[Tuple[int, int, float]]:
        """Fallback duplicate detection using simple text similarity"""
        duplicates = []
        
        for i in range(len(bullets)):
            for j in range(i + 1, len(bullets)):
                similarity = self._calculate_simple_similarity(
                    bullets[i].get("bullet_text", ""),
                    bullets[j].get("bullet_text", "")
                )
                
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        
        return duplicates

    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation using word overlap"""
        if not text1 or not text2:
            return 0.0
            
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


class DataEnricher:
    """Data enrichment component for canonical verb mapping and duplicate detection"""

    def __init__(self, enricher_config: Optional[Dict] = None):
        self.duplicate_detector = DuplicateDetector()
        # Use constants directly instead of EnricherConfig to avoid circular imports
        self.CANONICAL_VERBS = CANONICAL_VERBS
        self.enable_verb_canonicalization = True
        self.enable_skill_mapping = True
        self.duplicate_threshold = 0.9

    def _canonicalize_verbs(self, text: str) -> List[str]:
        """Extract canonical verbs from text using configured verb mapping"""
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(self, extracted_data: Dict, thematic_analysis: Optional[Dict] = None) -> Dict:
        """Enrich extracted data with canonical verbs and duplicate detection"""
        enriched_data = extracted_data.copy()
        
        # Process experience sections
        for section in enriched_data.get("experience_sections", []):
            for bullet in section.get("bullets", []):
                # Add canonical verbs
                bullet["canonical_verbs"] = self._canonicalize_verbs(bullet["bullet_text"])
                
                # Update provenance if enriched
                if bullet["canonical_verbs"]:
                    bullet["provenance"] = BulletProvenance.ENRICHED.value

        # Detect duplicates within each experience section
        for section in enriched_data.get("experience_sections", []):
            bullets = section.get("bullets", [])
            if len(bullets) > 1:
                duplicates = self.duplicate_detector.find_duplicates(bullets)
                if duplicates:
                    # Mark duplicate bullets
                    for idx1, idx2, similarity in duplicates:
                        if idx1 < len(bullets):
                            bullets[idx1]["is_duplicate"] = True
                            bullets[idx1]["duplicate_similarity"] = similarity
                        if idx2 < len(bullets):
                            bullets[idx2]["is_duplicate"] = True
                            bullets[idx2]["duplicate_similarity"] = similarity

        return enriched_data

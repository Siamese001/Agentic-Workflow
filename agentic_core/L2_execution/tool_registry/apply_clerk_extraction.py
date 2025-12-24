# Ownership: apps_rg / L2_execution
# -*- coding: utf-8 -*-
"""Clerk extraction for resume generation HOP-1."""

import logging
from typing import Any, Optional, Protocol, Dict, List, Tuple


class ClerkExtractor:
    """HOP-1: Extract structured data from master resume."""

    REQUIRED_KEYS = [
        "owner",
        "professional_experience",
        "education",
        "certifications_and_credentials",
        "strategic_and_technical_competencies",
    ]

    def __init__(self, master_resume: Dict) -> None:
        """Initialize the clerk extractor."""
        self.master_resume = master_resume
        self.hallucination_detector = HallucinationDetector()
        self._validate_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        """Extract and validate structured data from master resume."""
        experience_sections = self._build_experience_sections()

        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([b["bullet_text"] for b in section.get("bullets", [])])

        bullet_dicts = [{"bullet_text": b} for b in all_bullets]
        validation_results = self.hallucination_detector.detect(bullet_dicts)

        return {
            "experience_sections": experience_sections,
            "header": self.master_resume.get("header", {}),
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications", []),
        }, validation_results

    def _validate_structure(self) -> None:
        """Validate master resume has required keys."""
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")
        MISSING = [k for k in self.REQUIRED_KEYS if k not in self.master_resume]
        if MISSING: # Corrected variable name from 'missing' to 'MISSING'
            raise ValueError(f"Missing required keys: {', '.join(MISSING)}")

    def _build_experience_sections(self) -> List[Dict]:
        """Build structured experience_sections from master resume."""
        SECTIONS = []
        for exp in self.master_resume.get("experience", []):
            BULLETS = [
                {
                    "bullet_text": text,
                    "quantified_metrics": self._extract_metrics(text),
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.Verbatim.value,
                }
                for text in exp.get("bullets", [])
            ]
            SECTIONS.append({ # Corrected variable name from 'sections' to 'SECTIONS'
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", ""),
                "overview": exp.get("overview", ""),
                "bullets": BULLETS, # Corrected variable name from 'bullets' to 'BULLETS'
                "highlights": [b["bullet_text"] for b in BULLETS], # Corrected variable name
            })
        return SECTIONS # Corrected variable name from 'sections' to 'SECTIONS'

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract quantified metrics from bullet text."""
        PATTERNS = [
            r"\$\d+\.?\d*[MBK]\+?",
            r"\d+\.?\d*%",
            r"\d+\.?\d*[MBK]\+",
            r"\d{1,3}(?:,\d{3})+", # Fixed unterminated string literal
        ]
        METRICS = []
        import re # Added missing import for 're' module
        for pattern in PATTERNS: # Corrected variable name from 'patterns' to 'PATTERNS'
            METRICS.extend(re.findall(pattern, text))
        return METRICS # Corrected variable name from 'metrics' to 'METRICS'
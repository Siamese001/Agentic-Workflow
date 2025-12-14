
# Ownership: apps_rg / L2_execution
# -*- coding: utf-8 -*-
"""Clerk extraction for resume generation HOP-1."""

from typing import Dict, List, Tuple
import logging


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
        missing = [k for k in self.REQUIRED_KEYS if k not in self.master_resume]
        if missing:
            raise ValueError(f"Missing required keys: {', '.join(missing)}")

    def _build_experience_sections(self) -> List[Dict]:
        """Build structured experience_sections from master resume."""
        sections = []
        for exp in self.master_resume.get("experience", []):
            bullets = [
                {
                    "bullet_text": text,
                    "quantified_metrics": self._extract_metrics(text),
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.Verbatim.value,
                }
                for text in exp.get("bullets", [])
            ]
            sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", ""),
                "overview": exp.get("overview", ""),
                "bullets": bullets,
                "highlights": [b["bullet_text"] for b in bullets],
            })
        return sections

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract quantified metrics from bullet text."""
        patterns = [r"\$\d+\.?\d*[MBK]\+?",
            r"\d+\.?\d*%",
            r"\d+\.?\d*[MBK]\+",
            r"\d{1,
            3}(?:,
            \d{3})+"]
        metrics = []
        for pattern in patterns:
            metrics.extend(re.findall(pattern, text))
        return metrics

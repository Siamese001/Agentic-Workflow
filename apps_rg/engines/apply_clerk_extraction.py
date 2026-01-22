"""Clerk extraction for resume generation HOP-1."""


class ClerkExtractor:
    """HOP-1: Extract structured data from master resume."""

    REQUIRED_KEYS: Any = [
        "owner",
        "professional_experience",
        "education",
        "certifications_and_credentials",
        "strategic_and_technical_competencies",
    ]

    def __init__(self, master_resume: dict) -> None:
        """Initialize the clerk extractor."""
        self.master_resume = master_resume
        self.HallucinationDetectorAgent = HallucinationDetectorAgent()
        self._validate_structure()

    def extract(self) -> tuple[dict, list[ValidationResult]]:
        """Extract and validate structured data from master resume."""
        experience_sections: Any = self._build_experience_sections()
        all_bullets: Any = []
        for section in experience_sections:
            all_bullets.extend([b["bullet_text"] for b in section.get("bullets", [])])
        bullet_dicts: Any = [{"bullet_text": b} for b in all_bullets]
        validation_results: Any = self.HallucinationDetectorAgent.detect(bullet_dicts)
        return (
            {
                "experience_sections": experience_sections,
                "header": self.master_resume.get("header", {}),
                "education": self.master_resume.get("education", []),
                "certifications": self.master_resume.get("certifications", []),
            },
            validation_results,
        )

    def _validate_structure(self) -> None:
        """Validate master resume has required keys."""
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")
        MISSING = [k for k in self.REQUIRED_KEYS if k not in self.master_resume]
        if MISSING:
            raise ValueError(f"Missing required keys: {', '.join(MISSING)}")

    def _build_experience_sections(self) -> list[dict]:
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
            SECTIONS.append(
                {
                    "company": exp.get("company", ""),
                    "title": exp.get("title", ""),
                    "location": exp.get("location", ""),
                    "start_date": exp.get("start_date", ""),
                    "end_date": exp.get("end_date", ""),
                    "overview": exp.get("overview", ""),
                    "bullets": BULLETS,
                    "highlights": [b["bullet_text"] for b in BULLETS],
                }
            )
        return SECTIONS

    def _extract_metrics(self, text: str) -> list[str]:
        """Extract quantified metrics from bullet text."""
        PATTERNS = [
            "\\$\\d+\\.?\\d*[MBK]\\+?",
            "\\d+\\.?\\d*%",
            "\\d+\\.?\\d*[MBK]\\+",
            "\\d{1,3}(?:,\\d{3})+",
        ]
        METRICS = []
        import re

        for pattern in PATTERNS:
            METRICS.extend(re.findall(pattern, text))
        return METRICS

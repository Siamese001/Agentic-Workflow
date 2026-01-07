"""
ATSCompatibilityAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class ATSCompatibilityAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, ResumeAgent):
    """
    Validates ATS (Applicant Tracking System) compatibility.

    Checks:
    - No complex formatting
    - Standard section headers
    - Keyword optimization
    - No tables/graphics references
    """

    STANDARD_HEADERS = {
        "summary": ["summary", "professional summary", "profile", "objective"],
        "experience": ["experience", "work experience", "employment history", "work history"],
        "skills": ["skills", "technical skills", "core competencies", "expertise"],
        "education": ["education", "academic background", "qualifications"],
    }

    ATS_UNFRIENDLY_PATTERNS = [
        r'[│┃┆┇┊┋]',  # Box drawing characters
        r'[★☆●○◆◇■□▪▫]',  # Decorative bullets
        r'[\u2500-\u257F]',  # Box drawing
        r'<table',  # HTML tables
        r'<img',  # Images
    ]

    async def execute(self) -> None:
        self.log("Checking ATS compatibility...")

        resume = self.ctx.current_resume
        job_desc = self.ctx.JobDescription

        if not resume:
            self.record_fail("No resume to check")
            self.add_signal("ATS_FAILURE")
            return

        issues = []

        # Check for ATS-unfriendly patterns (use ensure_ascii=False to preserve unicode)
        full_content = json.dumps(resume, ensure_ascii=False)
        for pattern in self.ATS_UNFRIENDLY_PATTERNS:
            if re.search(pattern, full_content):
                issues.append(f"ATS-unfriendly pattern found: {pattern}")

        # Check section headers
        for section_name in resume.keys():
            if section_name.startswith("_"):
                continue

            normalized = section_name.lower().strip()
            is_standard = False

            for standard_section, variants in self.STANDARD_HEADERS.items():
                if normalized in variants or normalized == standard_section:
                    is_standard = True
                    break

            if not is_standard and normalized not in ["contact", "projects", "certifications", "achievements"]:
                issues.append(f"Non-standard section header: {section_name}")

        # Check keyword optimization if job description available
        if job_desc:
            keyword_score = self._calculate_keyword_score(resume, job_desc)
            if keyword_score < 0.3:
                issues.append(f"Low keyword match ({keyword_score:.0%})")

        if issues:
            self.record_fail(f"ATS issues: {len(issues)}", data=issues)
            self.add_signal("ATS_FAILURE")
        else:
            self.record_pass("ATS compatible")
            self.remove_signal("ATS_FAILURE")

    def _calculate_keyword_score(self, resume: Dict, job_desc: str) -> float:
        """Calculate keyword match score."""
        # Extract keywords from job description
        job_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_desc.lower()))

        # Common words to ignore
        stop_words = {"the", "and", "for", "with", "you", "are", "will", "have", "this", "that", "from", "they", "been", "were", "being", "their", "would", "could", "should", "about", "which", "when", "what", "where", "there", "here"}
        job_words -= stop_words

        if not job_words:
            return 1.0

        # Check resume content
        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)

        return matches / len(job_words)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

"""
Content Quality Validator - Deterministic Content Quality Validation

Zero-Ambiguity Standard: Renamed from content_quality_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Placeholder detection using regex patterns
- Basic skill validation with rule-based logic
- Resume text processing and normalization
- Quantified achievements analysis
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class QualityValidationResult:
    """Result of content quality validation."""

    passed: bool
    issues: list[str]
    score: float | None = None
    suggestions: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class ContentQualityValidator:
    """
    Pure deterministic content quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with content quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        self.placeholder_patterns = config.get(
            "placeholder_patterns",
            [r"\[.*?\]", r"\{.*?\}", r"<.*?>", r"\$.*?\$"],
        )
        self.quantified_patterns = config.get(
            "quantified_patterns",
            [
                r"\d+\s*(?:%|percent|percentages?)",
                r"\$\d+(?:,\d{3})*(?:\.\d{2})?",
                r"\d+\s*(?:years?|months?|days?)",
                r"\d+\s*(?:projects?|tasks?|items?)",
            ],
        )
        self.skill_keywords = config.get("skill_keywords", [])
        self.min_skill_matches = config.get("min_skill_matches", 3)

    def validate_content_quality(
        self,
        resume: dict[str, Any],
        job_desc: str | None = None,
    ) -> QualityValidationResult:
        """
        Validate content quality using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for skill matching

        Returns:
            QualityValidationResult with deterministic findings
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # Check for placeholders (deterministic regex matching)
        placeholder_issues = self._check_placeholders(resume)
        issues.extend(placeholder_issues)

        # Check quantified achievements (deterministic pattern matching)
        quantified_issues = self._check_quantified_achievements(resume)
        issues.extend(quantified_issues)

        # Validate skills with deterministic logic
        skill_issues, skill_suggestions = self._validate_skills(resume, job_desc)
        issues.extend(skill_issues)
        suggestions.extend(skill_suggestions)

        # Calculate overall quality score
        score = self._calculate_quality_score(issues, resume)

        return QualityValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            score=score,
            metadata={"validation_type": "deterministic"},
        )

    def _check_placeholders(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for placeholder text using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        resume_text = json.dumps(resume, ensure_ascii=False)

        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            if matches:
                issues.append(f"Found {len(matches)} placeholder(s): {pattern}")

        return issues

    def _check_quantified_achievements(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for quantified achievements using deterministic patterns.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        resume_text = json.dumps(resume, ensure_ascii=False)

        quantified_count = 0
        for pattern in self.quantified_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            quantified_count += len(matches)

        if quantified_count < 3:
            issues.append(f"Insufficient quantified achievements ({quantified_count} found)")

        return issues

    def _validate_skills(
        self,
        resume: dict[str, Any],
        job_desc: str | None = None,
    ) -> tuple[list[str], list[str]]:
        """
        Validate skills using deterministic rule-based logic.

        Moved to Deterministic: Pure string matching and validation
        """
        issues: list[str] = []
        suggestions: list[str] = []

        resume_text = json.dumps(resume).lower()

        # Count skill matches (deterministic string matching)
        skill_matches = 0
        matched_skills: set[str] = set()

        for skill in self.skill_keywords:
            if skill.lower() in resume_text:
                skill_matches += 1
                matched_skills.add(skill)

        if skill_matches < self.min_skill_matches:
            issues.append(f"Insufficient skill matches ({skill_matches} found)")

        # If job description provided, check alignment
        if job_desc:
            alignment_score = self._calculate_skill_alignment(matched_skills, job_desc)
            if alignment_score < 0.5:
                suggestions.append("Improve skill alignment with job description")

        return issues, suggestions

    def _calculate_skill_alignment(self, skills: set[str], job_desc: str) -> float:
        """
        Calculate skill alignment using deterministic text analysis.

        Moved to Deterministic: Pure text processing and calculation
        """
        if not skills:
            return 0.0

        job_desc_lower = job_desc.lower()
        aligned_skills = 0

        for skill in skills:
            if skill.lower() in job_desc_lower:
                aligned_skills += 1

        return aligned_skills / len(skills)

    def _calculate_quality_score(self, issues: list[str], resume: dict[str, Any]) -> float:
        """
        Calculate overall quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        base_score = 1.0

        # Deduct points for each issue
        base_score -= len(issues) * 0.1

        # Bonus points for comprehensive content
        resume_sections = len([k for k in resume.keys() if not k.startswith("_")])
        if resume_sections >= 5:
            base_score += 0.1

        # Bonus points for quantified achievements
        resume_text = json.dumps(resume, ensure_ascii=False)
        quantified_count = sum(
            len(re.findall(pattern, resume_text, re.IGNORECASE)) for pattern in self.quantified_patterns
        )
        if quantified_count >= 5:
            base_score += 0.1

        return max(0.0, min(1.0, base_score))

    def extract_resume_text(self, resume: dict[str, Any]) -> str:
        """
        Extract and normalize resume text for processing.

        Moved to Deterministic: Pure text extraction and normalization
        """
        # Convert resume to JSON and normalize
        text = json.dumps(resume, ensure_ascii=False)

        # Remove JSON structure characters
        text = re.sub(r'[{}"\[\],:]', " ", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def detect_formatting_issues(self, text: str) -> list[str]:
        """
        Detect formatting issues using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        """
        issues: list[str] = []

        # Check for excessive capitalization
        if re.search(r"[A-Z]{4,}", text):
            issues.append("Excessive capitalization detected")

        # Check for repeated characters
        if re.search(r"(.)\1{3,}", text):
            issues.append("Repeated characters detected")

        # Check for very short sentences
        sentences = re.split(r"[.!?]+", text)
        short_sentences = [s for s in sentences if len(s.strip()) < 5 and s.strip()]
        if len(short_sentences) > 3:
            issues.append("Too many very short sentences")

        return issues

"""
ATS Validator - Deterministic ATS Compatibility Validation

Zero-Ambiguity Standard: Renamed from ats_validation_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Pattern matching for ATS-unfriendly formats
- Section header validation
- Keyword scoring algorithm
- Text normalization and processing
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class ATSValidationResult:
    """Result of ATS validation with deterministic scoring."""

    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class AtsValidator:
    """
    Pure deterministic ATS validation logic.

    All methods in this class are 100% deterministic and can be
    executed without external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with ATS validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        self.standard_headers = config.get("standard_headers", {})
        self.ats_unfriendly_patterns = config.get("ats_unfriendly_patterns", [])
        self.allowed_non_standard_sections = config.get("allowed_non_standard_sections", [])
        self.keyword_config = config.get("keyword_optimization", {})
        self.min_score_threshold = self.keyword_config.get("min_score_threshold", 0.3)
        self.stop_words: set[str] = set(self.keyword_config.get("stop_words", []))

    def validate_ats_compatibility(
        self, resume: dict[str, Any], job_desc: str | None = None
    ) -> ATSValidationResult:
        """
        Validate ATS compatibility using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for keyword scoring

        Returns:
            ATSValidationResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AtsValidator.validate_ats_compatibility")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:AtsValidator.validate_ats_compatibility".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        issues.extend(self._check_ats_unfriendly_patterns(resume))
        issues.extend(self._validate_section_headers(resume))
        score = None
        if job_desc:
            score = self.calculate_keyword_score(resume, job_desc)
            if score < self.min_score_threshold:
                issues.append(f"Low keyword match ({score:.0%})")
        return ATSValidationResult(
            passed=len(issues) == 0, issues=issues, score=score, metadata={"validation_type": "deterministic"}
        )

    def _check_ats_unfriendly_patterns(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for ATS-unfriendly patterns using deterministic regex.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        full_content = json.dumps(resume, ensure_ascii=False)
        for pattern in self.ats_unfriendly_patterns:
            if re.search(pattern, full_content):
                issues.append(f"ATS-unfriendly pattern found: {pattern}")
        return issues

    def _validate_section_headers(self, resume: dict[str, Any]) -> list[str]:
        """
        Validate section headers using deterministic string comparison.

        Moved to Deterministic: Pure string validation logic
        """
        issues: list[str] = []
        for section_name in resume.keys():
            if section_name.startswith("_"):
                continue
            normalized = section_name.lower().strip()
            is_standard = False
            for standard_section, variants in self.standard_headers.items():
                if normalized in variants or normalized == standard_section:
                    is_standard = True
                    break
            if not is_standard and normalized not in self.allowed_non_standard_sections:
                issues.append(f"Non-standard section header: {section_name}")
        return issues

    def calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical calculation
        """
        job_words = set(re.findall("\\b[a-zA-Z]{3,}\\b", job_desc.lower()))
        job_words -= self.stop_words
        if not job_words:
            return 1.0
        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)
        return matches / len(job_words)

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing.

        Moved to Deterministic: Pure string manipulation
        """
        text = re.sub("\\s+", " ", text.strip())
        return text.lower()

    # guardian: allow-magic-config
    def extract_keywords(self, text: str, min_length: int = 3) -> set[str]:
        """
        Extract keywords from text using deterministic regex.

        Moved to Deterministic: Pure pattern extraction
        """
        words = set(re.findall(f"\\b[a-zA-Z]{{{min_length},}}\\b", text.lower()))
        return words - self.stop_words

    def validate_formatting(self, content: str) -> list[str]:
        """
        Validate content formatting using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        """
        issues: list[str] = []
        if re.search("[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]", content):
            issues.append("Contains control characters")
        if re.search("\\n{3,}", content):
            issues.append("Excessive line breaks")
        if "\r\n" in content and "\n" in content and (content.count("\r\n") != content.count("\n")):
            issues.append("Mixed line ending formats")
        return issues

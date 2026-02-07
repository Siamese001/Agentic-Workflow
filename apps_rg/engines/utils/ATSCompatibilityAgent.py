"""
ATSCompatibilityAgent - Facade Shell for Zero-Loss Consolidation.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
Converted to Facade: 2026-01-31 (Phase 2 Consolidation)

FACADE PATTERN: Delegates to UnifiedAgent while preserving 100% legacy compatibility.
All original imports and signatures work without modification.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    AgentCategory,
    UnifiedAgent,
    ValidationResult,
    ValidatorStrategy,
)
from apps_rg.shared.core.RGAgentBase import RGAgentBase
from apps_shared.config.config_loader_config import load_agent_config


class ATSValidatorStrategy(ValidatorStrategy):
    """ATS-specific validation strategy preserving original logic."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with ATS-specific configuration."""
        super().__init__(config)
        self.STANDARD_HEADERS = config.get("standard_headers", {})
        self.ATS_UNFRIENDLY_PATTERNS = config.get("ats_unfriendly_patterns", [])
        self.allowed_non_standard_sections = config.get("allowed_non_standard_sections", [])
        self.keyword_config = config.get("keyword_optimization", {})
        self.min_score_threshold = self.keyword_config.get("min_score_threshold", 0.3)
        self.stop_words = set(self.keyword_config.get("stop_words", []))

    async def execute(self, agent: UnifiedAgent, **kwargs: Any) -> ValidationResult:
        """Execute ATS-specific validation logic."""
        agent.log_info("Checking ATS compatibility...")

        # Get resume from context or kwargs
        resume = kwargs.get("resume") or self._get_resume_from_context(agent)
        job_desc = kwargs.get("job_desc") or self._get_job_desc_from_context(agent)

        if not resume:
            return ValidationResult(
                passed=False,
                issues=["No resume to check"],
                suggestions=[],
            )

        issues: list[str] = []

        # Check for ATS-unfriendly patterns
        full_content: str = json.dumps(resume, ensure_ascii=False)
        for pattern in self.ATS_UNFRIENDLY_PATTERNS:
            if re.search(pattern, full_content):
                issues.append(f"ATS-unfriendly pattern found: {pattern}")

        # Check section headers
        for section_name in resume.keys():
            if section_name.startswith("_"):
                continue

            normalized: str = section_name.lower().strip()
            is_standard: bool = False

            for standard_section, variants in self.STANDARD_HEADERS.items():
                if normalized in variants or normalized == standard_section:
                    is_standard = True
                    break

            if not is_standard and normalized not in self.allowed_non_standard_sections:
                issues.append(f"Non-standard section header: {section_name}")

        # Check keyword optimization if job description available
        score = None
        if job_desc:
            score = self._calculate_keyword_score(resume, job_desc)
            if score < self.min_score_threshold:
                issues.append(f"Low keyword match ({score:.0%})")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            suggestions=[],
            score=score,
            metadata={"agent": "ATSCompatibilityAgent"},
        )

    def _get_resume_from_context(self, agent: UnifiedAgent) -> dict[str, Any] | None:
        """Get resume from agent context."""
        ctx = getattr(agent, "ctx", None)
        if ctx:
            return getattr(ctx, "current_resume", None)
        return None

    def _get_job_desc_from_context(self, agent: UnifiedAgent) -> str | None:
        """Get job description from agent context."""
        ctx = getattr(agent, "ctx", None)
        if ctx:
            return getattr(ctx, "JobDescription", None)
        return None

    def _calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score between resume and job description.

        [META-LEARNING] Enhanced with caching:
        - Caches keyword analysis results for similar resumes
        - Recalls scoring patterns for similar job descriptions
        - Optimizes repeated validations
        """
        # Create cache key from resume and job description signatures
        resume_sig = self._get_resume_signature(resume)
        job_sig = self._get_job_signature(job_desc)
        cache_key = f"ats_score:{resume_sig}:{job_sig}"

        # Try to get cached result
        if hasattr(self, "_agent") and hasattr(self._agent, "ml_cache_get"):
            cached_score = self._agent.ml_cache_get(cache_key)
            if cached_score is not None:
                self._agent.log_debug(f"[ATS] Using cached score: {cached_score:.0%}")
                return cached_score

        # Calculate score
        job_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_desc.lower()))
        job_words -= self.stop_words

        if not job_words:
            return 1.0

        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)
        score = matches / len(job_words)

        # Cache the result (TTL: 30 minutes)
        if hasattr(self, "_agent") and hasattr(self._agent, "ml_cache_set"):
            self._agent.ml_cache_set(cache_key, score, ttl=1800)

        return score

    def _get_resume_signature(self, resume: dict[str, Any]) -> str:
        """Generate a signature for resume caching."""
        # Use section names and lengths as signature
        sections = [(k, len(str(v))) for k, v in resume.items() if not k.startswith("_")]
        return str(hash(tuple(sorted(sections))) % 10000)

    def _get_job_signature(self, job_desc: str) -> str:
        """Generate a signature for job description caching."""
        # Use first 200 chars and word count as signature
        preview = job_desc[:200]
        word_count = len(job_desc.split())
        return str(hash((preview, word_count)) % 10000)


@dataclass
class ATSCompatibilityAgent(RGAgentBase):
    """
    Validates ATS (Applicant Tracking System) compatibility.

    FACADE SHELL: Delegates to UnifiedAgent with ATSValidatorStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Checks:
    - No complex formatting
    - Standard section headers
    - Keyword optimization
    - No tables/graphics references
    """

    _unified_strategy: ATSValidatorStrategy | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize ATS compatibility agent facade."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("ats_compatibility")

        # Initialize unified strategy with ATS-specific logic
        self._unified_strategy = ATSValidatorStrategy(self._config)

        # Preserve legacy interface attributes
        self.STANDARD_HEADERS = self._config.get("standard_headers", {})
        self.ATS_UNFRIENDLY_PATTERNS = self._config.get("ats_unfriendly_patterns", [])
        self.allowed_non_standard_sections = self._config.get("allowed_non_standard_sections", [])
        self.keyword_config = self._config.get("keyword_optimization", {})
        self.min_score_threshold = self.keyword_config.get("min_score_threshold", 0.3)
        self.stop_words = set(self.keyword_config.get("stop_words", []))

    async def execute(self) -> None:
        """
        Execute ATS compatibility check - FACADE DELEGATION.

        Validates resume for:
        - ATS-unfriendly formatting patterns
        - Standard section headers
        - Keyword optimization against job description

        Raises:
            ATS_FAILURE signal if compatibility issues found
        """
        self.log("Checking ATS compatibility...")

        # Get data from context
        resume = getattr(self.ctx, "current_resume", None) if hasattr(self, "ctx") else None
        job_desc = getattr(self.ctx, "JobDescription", None) if hasattr(self, "ctx") else None

        # Create a mock unified agent for strategy execution
        class MockUnifiedAgent:
            def __init__(self, ctx: Any) -> None:
                self.ctx = ctx
                self._category = AgentCategory.VALIDATOR

            def log_info(self, msg: str) -> None:
                pass

        mock_agent = MockUnifiedAgent(self.ctx if hasattr(self, "ctx") else None)

        # Execute via unified strategy
        result: ValidationResult = await self._unified_strategy.execute(
            mock_agent, resume=resume, job_desc=job_desc
        )

        # Preserve legacy signal handling
        if not result.passed:
            self.record_fail(f"ATS issues: {len(result.issues)}", data=result.issues)
            self.add_signal("ATS_FAILURE")
        else:
            self.record_pass("ATS compatible")
            self.remove_signal("ATS_FAILURE")

    def _calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score - LEGACY COMPATIBILITY METHOD.

        Args:
            resume: Resume data dictionary
            job_desc: Job description text

        Returns:
            Float between 0.0 and 1.0 representing keyword match percentage
        """
        return self._unified_strategy._calculate_keyword_score(resume, job_desc)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, int]:
        """
        Autonomous healing method - FACADE DELEGATION.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by ATSCompatibilityAgent."""
        violation_type = violation.get("type", "unknown")
        return {
            "status": "skipped",
            "details": f"ATSCompatibilityAgent heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }

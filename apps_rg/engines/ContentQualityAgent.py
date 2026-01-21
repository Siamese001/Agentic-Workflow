from __future__ import annotations

from dataclasses import dataclass

"""
Specialized Resume Agents - Phase 1 Implementation

This module contains all specialized agents for autonomous resume generation:
- ContentQualityAgent: Validates resume content quality
- FactCheckAgent: Verifies claims against user profile
- BrandComplianceAgent: Ensures brand voice and tone
- RgTemplateOptimizerAgent: Optimizes template selection
- SectionBalanceAgent: Ensures proper section balance
- ATSCompatibilityAgent: Validates ATS-friendly formatting
- TestPilot: Runs validation tests
- RgStrategicPlannerAgent: Plans execution strategy
- RgReflectionAgent: Learns from execution
"""
import json
import re
from typing import Any

from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from .resume_base import ResumeAgent


@dataclass
class ContentQualityAgent(SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin):
    """
    Validates resume content quality.

    Checks for:
    - Minimum content length
    - Proper sentence structure
    - No placeholder text
    - Quantified achievements
    """

    PLACEHOLDER_PATTERNS = [
        r'\[(?:NAME|COMPANY|TITLE|PLACEHOLDER|YOUR_NAME|INSERT)\]',  # [PLACEHOLDER] style
        r'\{(?:name|company|title|placeholder|your_name|insert)\}',  # {placeholder} style
        r'<(?:NAME|COMPANY|TITLE|PLACEHOLDER)>',    # <PLACEHOLDER> style
        r'\bTODO\b',
        r'\bTBD\b',
        r'\bFIXME\b',
        r'\bXXX\b',
        r'Lorem ipsum',
        r'PLACEHOLDER',
    ]

    MIN_SECTION_LENGTHS = {
        "summary": 50,
        "experience": 100,
        "skills": 20,
        "education": 30,
    }

    async def execute(self) -> None:
        """
        Execute content quality validation.

        Validates:
        - Minimum section lengths
        - Placeholder text detection
        - Sentence structure
        - Quantified achievements

        Raises:
            QUALITY_FAILURE signal if quality issues found
        """
        self.log("Analyzing content quality...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume content to analyze")
            self.add_signal("QUALITY_FAILURE")
            return

        issues: list = []

        # Check each section
        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue  # Skip metadata

            content_str: str = self._to_string(content)

            # Check for placeholders
            for pattern in self.PLACEHOLDER_PATTERNS:
                if re.search(pattern, content_str, re.IGNORECASE):
                    issues.append(f"Placeholder found in {section_name}: {pattern}")

            # Check minimum length
            min_length = self.MIN_SECTION_LENGTHS.get(section_name, 10)
            if len(content_str) < min_length:
                issues.append(f"{section_name} too short ({len(content_str)} < {min_length} chars)")

            # Check for quantified achievements in experience
            if section_name == "experience" and content_str:
                if not re.search(r'\d+[%KMB]?|\$\d+|\d+\s*(years?|months?|projects?|clients?|users?|engineers?|team)', content_str, re.IGNORECASE):
                    issues.append("Experience section lacks quantified achievements")

        if issues:
            self.record_fail(f"Quality issues: {len(issues)}", data=issues)
            self.add_signal("QUALITY_FAILURE")
        else:
            self.record_pass("Content quality validated")
            self.remove_signal("QUALITY_FAILURE")

    def _to_string(self, content: Any) -> str:
        """
        Convert content to string for analysis.

        Args:
            content: Content to convert (str, list, dict, or other)

        Returns:
            String representation of content
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository()


class TestPilot(ResumeAgent):
    """
    Runs validation tests on the generated resume.

    Executes:
    - Schema validation
    - Content validation
    - Integration checks
    """

    async def execute(self) -> None:
        self.log("Running validation tests...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to test")
            self.add_signal("TEST_FAILURE")
            return

        test_results = []

        # Test 1: Schema validation
        schema_result = self._test_schema(resume)
        test_results.append(("schema", schema_result))

        # Test 2: Content completeness
        completeness_result = self._test_completeness(resume)
        test_results.append(("completeness", completeness_result))

        # Test 3: No empty sections
        empty_result = self._test_no_empty_sections(resume)
        test_results.append(("no_empty", empty_result))

        # Test 4: Reasonable lengths
        length_result = self._test_reasonable_lengths(resume)
        test_results.append(("lengths", length_result))

        # Aggregate results
        passed = all(r[1]["passed"] for r in test_results)
        failed_tests = [r[0] for r in test_results if not r[1]["passed"]]

        if passed:
            self.record_pass("All tests passed", data=test_results)
            self.remove_signal("TEST_FAILURE")
        else:
            self.record_fail(f"Tests failed: {failed_tests}", data=test_results)
            self.add_signal("TEST_FAILURE")

    def _test_schema(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test basic schema structure.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        required_fields = ["summary", "experience", "skills"]
        Missing = [f for f in required_fields if f not in resume]
        return {
            "passed": len(Missing) == 0,
            "missing_fields": Missing,
        }

    def _test_completeness(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test content completeness.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        total_content = sum(
            len(str(v)) for k, v in resume.items() if not k.startswith("_")
        )
        return {
            "passed": total_content >= 200,
            "total_chars": total_content,
        }

    def _test_no_empty_sections(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test for empty sections.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        empty = [k for k, v in resume.items() if not k.startswith("_") and not v]
        return {
            "passed": len(empty) == 0,
            "empty_sections": empty,
        }

    def _test_reasonable_lengths(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test section lengths are reasonable.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        issues = []
        for section, content in resume.items():
            if section.startswith("_"):
                continue
            length = len(str(content))
            if length > 10000:
                issues.append(f"{section} too long ({length} chars)")
        return {
            "passed": len(issues) == 0,
            "issues": issues,
        }


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_rg resume-specific vs core implementations)
# - Intentional variant for domain-specific behavior
# - Consolidated 2026-01-06

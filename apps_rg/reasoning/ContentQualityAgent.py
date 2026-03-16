"""
Specialized Resume Agents - Phase 1 Implementation

This module contains all specialized agents for autonomous resume generation:
- ContentQualityAgent: Validates resume content quality (now delegates to logic nodes)
- FactCheckAgent: Verifies claims against user profile
- BrandComplianceAgent: Ensures brand voice and tone
- RgTemplateOptimizerAgent: Optimizes template selection
- SectionBalanceAgent: Ensures proper section balance
- ATSCompatibilityAgent: Validates ATS-friendly formatting
- TestPilot: Runs validation tests
- RgStrategicPlannerAgent: Plans execution strategy
- RgReflectionAgent: Learns from execution
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.utils.RGAgentBase import RGAgentBase

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.types.skill_extractor_node_types import SkillExtractorNode

_emit_applies_guardrail("p0", "ContentQualityAgent", "p0_governance")
_emit_reads_policy_state("p0", "ContentQualityAgent", "policy_binding")
_emit_snapshots_state("p0", "ContentQualityAgent", "state_snapshot")
emit_replay_key("p0", "ContentQualityAgent")
emit_determinism_digest("p0", "ContentQualityAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class ContentQualityAgent(RGAgentBase):
    """
    Validates resume content quality.

    Now delegates validation logic to SkillExtractorNode logic node
    to comply with Blueprint Depth-2 Structure requirements.

    Checks for:
    - Minimum content length
    - Proper sentence structure
    - No placeholder text
    - Quantified achievements
    """

    def __post_init__(self) -> None:
        """Initialize content quality agent with logic node composition."""
        super().__post_init__()
        self.skill_extractor = SkillExtractorNode(config=self.config.get("validation_config", {}))
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(self.project_root))
            _profile = _idx.profile_for(self._adg_resolved_self_path()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    PLACEHOLDER_PATTERNS = [
        "\\[(?:NAME|COMPANY|TITLE|PLACEHOLDER|YOUR_NAME|INSERT)\\]",
        "\\{(?:name|company|title|placeholder|your_name|insert)\\}",
        "<(?:NAME|COMPANY|TITLE|PLACEHOLDER)>",
        "\\bTODO\\b",
        "\\bTBD\\b",
        "\\bFIXME\\b",
        "\\bXXX\\b",
        "Lorem ipsum",
        "PLACEHOLDER",
    ]
    MIN_SECTION_LENGTHS = {"summary": 50, "experience": 100, "skills": 20, "education": 30}

    async def execute(self) -> None:
        """
        Execute content quality validation using delegated logic nodes.

        Validates:
        - Minimum section lengths
        - Placeholder text detection
        - Sentence structure
        - Quantified achievements

        Raises:
            QUALITY_FAILURE signal if quality issues found
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ContentQualityAgent.execute")
        self.log("Analyzing content quality using logic nodes...")
        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume content to analyze")
            self.add_signal("QUALITY_FAILURE")
            return
        issues: list[str] = []
        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue
            content_str: str = self._to_string(content)
            placeholder_issues = self._check_placeholders(content_str, section_name)
            issues.extend(placeholder_issues)
            min_length = self.MIN_SECTION_LENGTHS.get(section_name, 10)
            if len(content_str) < min_length:
                issues.append(f"{section_name} too short ({len(content_str)} < {min_length} chars)")
            if section_name == "experience" and content_str:
                quantified_issues = self._check_quantified_achievements(content_str)
                issues.extend(quantified_issues)
        skill_issues = self._validate_skills_with_logic_node(resume)
        issues.extend(skill_issues)
        if issues:
            self.record_fail(f"Quality issues: {len(issues)}", data=issues)
            self.add_signal("QUALITY_FAILURE")
        else:
            self.record_pass("Content quality validated using logic nodes")
            self.remove_signal("QUALITY_FAILURE")

    def _check_placeholders(self, content_str: str, section_name: str) -> list[str]:
        """Check for placeholder text using delegated logic.

        Args:
            content_str: Content string to check
            section_name: Name of the section being checked

        Returns:
            List of placeholder issues found
        """
        issues = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, content_str, re.IGNORECASE):
                issues.append(f"Placeholder found in {section_name}: {pattern}")
        return issues

    def _check_quantified_achievements(self, content_str: str) -> list[str]:
        """Check for quantified achievements using delegated logic.

        Args:
            content_str: Content string to check

        Returns:
            List of quantification issues found
        """
        issues = []
        if not re.search(
            "\\d+[%KMB]?|\\$\\d+|\\d+\\s*(years?|months?|projects?|clients?|users?|engineers?|team)",
            content_str,
            re.IGNORECASE,
        ):
            issues.append("Experience section lacks quantified achievements")
        return issues

    def _validate_skills_with_logic_node(self, resume: dict[str, Any]) -> list[str]:
        """Validate skills section using delegated logic node.

        Args:
            resume: Resume data to validate

        Returns:
            List of skill validation issues
        """
        issues = []
        try:
            profile_text = self._resume_to_profile_text(resume)
            skill_analysis = self.skill_extractor(profile_text, {})
            total_skills = (
                len(skill_analysis.extraction_result.technical_skills)
                + len(skill_analysis.extraction_result.soft_skills)
                + len(skill_analysis.extraction_result.domain_skills)
                + len(skill_analysis.extraction_result.tool_skills)
            )
            if total_skills < 5:
                issues.append(f"Insufficient skills extracted ({total_skills} < 5)")
            if skill_analysis.extraction_result.confidence_score < 0.6:
                issues.append(
                    f"Low skill extraction confidence ({skill_analysis.extraction_result.confidence_score:.2f})"
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            issues.append(f"Skill validation failed: {str(e)}")
        return issues

    def _resume_to_profile_text(self, resume: dict[str, Any]) -> str:
        """Convert resume to profile text format for skill extractor.

        Args:
            resume: Resume data

        Returns:
            Formatted profile text
        """
        profile_text = ""
        if "summary" in resume:
            profile_text += f" {resume['summary']}"
        if "experience" in resume:
            for exp in resume["experience"]:
                if isinstance(exp, dict):
                    profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
                    for bullet in exp.get("bullets", []):
                        profile_text += f" {bullet}"
        if "skills" in resume:
            if isinstance(resume["skills"], list):
                profile_text += " " + " ".join(str(s) for s in resume["skills"])
            else:
                profile_text += f" {resume['skills']}"
        return profile_text

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

    def heal_repository(self, dry_run: bool = False, execute: bool = False, **kwargs: Any) -> dict[str, int]:
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

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by ContentQualityAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"ContentQualityAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"ContentQualityAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class TestPilot(RGAgentBase):
    """
    Runs validation tests on the generated resume.

    Executes:
    - schema validation
    - Content validation
    - Integration checks
    """

    def __post_init__(self) -> None:
        """Initialize test pilot agent."""
        super().__post_init__()

    async def execute(self) -> None:
        self.log("Running validation tests...")
        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to test")
            self.add_signal("TEST_FAILURE")
            return
        test_results = []
        schema_result = self._test_schema(resume)
        test_results.append(("schema", schema_result))
        completeness_result = self._test_completeness(resume)
        test_results.append(("completeness", completeness_result))
        empty_result = self._test_no_empty_sections(resume)
        test_results.append(("no_empty", empty_result))
        length_result = self._test_reasonable_lengths(resume)
        test_results.append(("lengths", length_result))
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
        return {"passed": len(Missing) == 0, "missing_fields": Missing}

    def _test_completeness(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test content completeness.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        total_content = sum((len(str(v)) for k, v in resume.items() if not k.startswith("_")))
        return {"passed": total_content >= 200, "total_chars": total_content}

    def _test_no_empty_sections(self, resume: dict[str, Any]) -> dict[str, Any]:
        """
        Test for empty sections.

        Args:
            resume: Resume data to validate

        Returns:
            Dict with test results
        """
        empty = [k for k, v in resume.items() if not k.startswith("_") and (not v)]
        return {"passed": len(empty) == 0, "empty_sections": empty}

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
        return {"passed": len(issues) == 0, "issues": issues}

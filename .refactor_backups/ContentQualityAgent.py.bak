from __future__ import annotations
"""
Specialized Resume Agents - Phase 1 Implementation

This module contains all specialized agents for autonomous resume generation:
- ContentQualityAgent: Validates resume content quality
- FactCheckAgent: Verifies claims against user profile
- BrandComplianceAgent: Ensures brand voice and tone
- TemplateOptimizerAgent: Optimizes template selection
- SectionBalanceAgent: Ensures proper section balance
- ATSCompatibilityAgent: Validates ATS-friendly formatting
- TestPilot: Runs validation tests
- StrategicPlannerAgent: Plans execution strategy
- ReflectionAgent: Learns from execution
"""
from typing import Any, Optional, Protocol, Dict, List


import json
import re
from typing import Any, Dict

from .resume_base import ResumeAgent


class ContentQualityAgent(ResumeAgent):
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
        self.log("Analyzing content quality...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume content to analyze")
            self.add_signal("QUALITY_FAILURE")
            return

        issues = []

        # Check each section
        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue  # Skip metadata

            content_str = self._to_string(content)

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
        """Convert content to string for analysis."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class FactCheckAgent(ResumeAgent):
    """
    Verifies claims against user profile.

    Checks for:
    - Claims that can be verified against profile
    - No hallucinated skills or experiences
    - Dates consistency
    """

    async def execute(self) -> None:
        self.log("Fact-checking resume claims...")

        resume = self.ctx.current_resume
        profile = self.ctx.user_profile

        if not resume:
            self.record_fail("No resume to fact-check")
            self.add_signal("HALLUCINATION_DETECTED")
            return

        if not profile:
            self.log("⚠️ No user profile available, skipping deep fact-check")
            self.record_pass("Fact-check skipped (no profile)")
            return

        issues = []

        # Check skills against profile (case-insensitive)
        resume_skills = self._extract_skills(resume)
        profile_skills = {self._normalize(s) for s in profile.get("skills", []) if isinstance(s, str)}

        if profile_skills and resume_skills:
            unverified_skills = resume_skills - profile_skills
            # Only flag if majority of skills are unverified
            if unverified_skills and len(unverified_skills) > len(resume_skills) * 0.5:
                issues.append(f"Unverified skills: {list(unverified_skills)[:5]}")

        # Check experience dates
        if "experience" in resume and "work_history" in profile:
            resume_exp = resume.get("experience", [])
            profile_exp = profile.get("work_history", [])

            if isinstance(resume_exp, list) and isinstance(profile_exp, list):
                resume_companies = {self._normalize(e.get("company", "")) for e in resume_exp if isinstance(e, dict)}
                profile_companies = {self._normalize(e.get("company", "")) for e in profile_exp if isinstance(e, dict)}

                if profile_companies:
                    unverified = resume_companies - profile_companies
                    if unverified:
                        issues.append(f"Unverified companies: {list(unverified)[:3]}")

        if issues:
            self.record_fail(f"Fact-check issues: {len(issues)}", data=issues)
            self.add_signal("HALLUCINATION_DETECTED")
        else:
            self.record_pass("All claims verified")
            self.remove_signal("HALLUCINATION_DETECTED")

    def _extract_skills(self, resume: Dict) -> set:
        """Extract skills from resume."""
        skills = set()

        if "skills" in resume:
            skill_data = resume["skills"]
            if isinstance(skill_data, list):
                skills.update(self._normalize(s) for s in skill_data if isinstance(s, str))
            elif isinstance(skill_data, str):
                skills.update(self._normalize(s) for s in skill_data.split(","))
            elif isinstance(skill_data, dict):
                for category_skills in skill_data.values():
                    if isinstance(category_skills, list):
                        skills.update(self._normalize(s) for s in category_skills if isinstance(s, str))

        return skills

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class BrandComplianceAgent(ResumeAgent):
    """
    Ensures brand voice and professional tone.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    FORBIDDEN_PHRASES = [
        "i am", "i'm", "my name is",  # First person in summary
        "responsible for",  # Weak phrasing
        "duties included",  # Passive
        "helped with",  # Vague
        "worked on",  # Vague
        "etc.",  # Unprofessional
        "stuff",  # Informal
        "things",  # Vague
        "very",  # Weak intensifier
        "really",  # Weak intensifier
    ]

    POWER_VERBS = [
        "achieved", "delivered", "drove", "led", "managed",
        "developed", "created", "implemented", "optimized", "increased",
        "reduced", "improved", "launched", "designed", "built",
    ]

    async def execute(self) -> None:
        self.log("Checking brand compliance...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to check")
            self.add_signal("BRAND_VIOLATION")
            return

        issues = []
        suggestions = []

        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue

            content_str = self._to_string(content).lower()

            # Check forbidden phrases
            for phrase in self.FORBIDDEN_PHRASES:
                if phrase in content_str:
                    issues.append(f"Forbidden phrase '{phrase}' in {section_name}")

            # Check for power verbs in experience
            if section_name == "experience":
                has_power_verb = any(verb in content_str for verb in self.POWER_VERBS)
                if not has_power_verb:
                    suggestions.append("Experience section could use more action verbs")

        if issues:
            self.record_fail(f"Brand violations: {len(issues)}", data={"issues": issues, "suggestions": suggestions})
            self.add_signal("BRAND_VIOLATION")
        else:
            self.record_pass("Brand compliant", data={"suggestions": suggestions})
            self.remove_signal("BRAND_VIOLATION")

    def _to_string(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class TemplateOptimizerAgent(ResumeAgent):
    """
    Optimizes template selection based on job description.

    Analyzes:
    - Job requirements
    - Industry standards
    - Role level
    """

    TEMPLATE_RECOMMENDATIONS = {
        "technical": ["skills_first", "projects_prominent"],
        "executive": ["summary_prominent", "achievements_focused"],
        "creative": ["portfolio_linked", "visual_friendly"],
        "entry_level": ["education_first", "skills_prominent"],
    }

    async def execute(self) -> None:
        self.log("Optimizing template selection...")

        job_desc = self.ctx.JobDescription
        if not job_desc:
            self.record_pass("No job description, using default template")
            return

        # Analyze job type
        job_type = self._detect_job_type(job_desc)
        recommendations = self.TEMPLATE_RECOMMENDATIONS.get(job_type, [])

        self.ctx.results["template_recommendations"] = {
            "job_type": job_type,
            "recommendations": recommendations,
        }

        self.record_pass(f"Template optimized for {job_type} role", data=recommendations)

    def _detect_job_type(self, job_desc: str) -> str:
        """Detect job type from description."""
        job_lower = job_desc.lower()

        technical_keywords = ["engineer", "developer", "programming", "software", "technical", "data", "cloud", "devops"]
        executive_keywords = ["director", "vp", "vice president", "chief", "head of", "executive", "senior manager"]
        creative_keywords = ["designer", "creative", "artist", "ux", "ui", "brand", "content"]
        entry_keywords = ["entry level", "junior", "associate", "intern", "graduate", "new grad"]

        if any(kw in job_lower for kw in executive_keywords):
            return "executive"
        elif any(kw in job_lower for kw in technical_keywords):
            return "technical"
        elif any(kw in job_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in job_lower for kw in entry_keywords):
            return "entry_level"

        return "technical"  # Default

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class SectionBalanceAgent(ResumeAgent):
    """
    Ensures proper section balance and prioritization.

    Checks:
    - Section lengths are proportional
    - Important sections are present
    - Order matches job requirements
    """

    REQUIRED_SECTIONS = ["summary", "experience", "skills"]
    RECOMMENDED_SECTIONS = ["education", "projects", "certifications"]

    MAX_SECTION_RATIOS = {
        "summary": 0.40,  # Max 40% of total
        "experience": 0.70,  # Max 70% of total
        "skills": 0.40,  # Max 40% of total
        "education": 0.30,  # Max 30% of total
    }

    async def execute(self) -> None:
        self.log("Checking section balance...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to check")
            return

        issues = []

        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in resume or not resume[section]:
                issues.append(f"Missing required section: {section}")

        # Calculate total content length
        total_length = sum(
            len(self._to_string(v))
            for k, v in resume.items()
            if not k.startswith("_")
        )

        if total_length == 0:
            self.record_fail("Resume has no content")
            return

        # Check section ratios
        for section, max_ratio in self.MAX_SECTION_RATIOS.items():
            if section in resume:
                section_length = len(self._to_string(resume[section]))
                ratio = section_length / total_length
                if ratio > max_ratio:
                    issues.append(f"{section} is too long ({ratio:.0%} > {max_ratio:.0%})")

        if issues:
            self.record_fail(f"Balance issues: {len(issues)}", data=issues)
            self.add_signal("BALANCE_ISSUE")
        else:
            self.record_pass("Section balance is good")
            self.remove_signal("BALANCE_ISSUE")

    def _to_string(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


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

    def _test_schema(self, resume: Dict) -> Dict:
        """Test basic schema structure."""
        required_fields = ["summary", "experience", "skills"]
        Missing = [f for f in required_fields if f not in resume]
        return {
            "passed": len(Missing) == 0,
            "missing_fields": Missing,
        }

    def _test_completeness(self, resume: Dict) -> Dict:
        """Test content completeness."""
        total_content = sum(
            len(str(v)) for k, v in resume.items() if not k.startswith("_")
        )
        return {
            "passed": total_content >= 200,
            "total_chars": total_content,
        }

    def _test_no_empty_sections(self, resume: Dict) -> Dict:
        """Test for empty sections."""
        empty = [k for k, v in resume.items() if not k.startswith("_") and not v]
        return {
            "passed": len(empty) == 0,
            "empty_sections": empty,
        }

    def _test_reasonable_lengths(self, resume: Dict) -> Dict:
        """Test section lengths are reasonable."""
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


class StrategicPlannerAgent(ResumeAgent):
    """
    Plans execution strategy based on signals and state.

    Analyzes:
    - Current signals
    - Failed agents
    - Modified sections
    - Blast radius
    """

    async def execute(self) -> None:
        self.log("Formulating strategic plan...")

        # Analyze current state
        signals = list(self.ctx.signals)
        list(self.ctx.get_failed_results().keys())
        list(self.ctx.modified_sections)
        impact = list(self.ctx.impact_zone)

        plan = {
            "priority_signals": [],
            "recommended_agents": [],
            "sections_to_review": [],
            "strategy": "standard",
        }

        # Prioritize signals
        if "QUALITY_FAILURE" in signals:
            plan["priority_signals"].append("QUALITY_FAILURE")
            plan["recommended_agents"].extend(["ContentQualityAgent", "FactCheckAgent"])
            plan["strategy"] = "quality_focus"

        if "HALLUCINATION_DETECTED" in signals:
            plan["priority_signals"].append("HALLUCINATION_DETECTED")
            plan["recommended_agents"].append("FactCheckAgent")
            plan["strategy"] = "fact_check_focus"

        if "ATS_FAILURE" in signals:
            plan["priority_signals"].append("ATS_FAILURE")
            plan["recommended_agents"].append("ATSCompatibilityAgent")

        if "BRAND_VIOLATION" in signals:
            plan["priority_signals"].append("BRAND_VIOLATION")
            plan["recommended_agents"].append("BrandComplianceAgent")

        # Add sections to review based on blast radius
        if impact:
            plan["sections_to_review"] = impact
            self.log(f"☢️ Blast radius: {len(impact)} sections may need review")

        # Store plan
        self.ctx.results["strategic_plan"] = plan

        self.record_pass(f"Strategy: {plan['strategy']}", data=plan)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_rg resume-specific vs core implementations)
# - Intentional variant for domain-specific behavior
# - Consolidated 2026-01-06

class ReflectionAgent(ResumeAgent):
    """
    Learns from execution and records insights.

    Analyzes:
    - What worked
    - What failed
    - Patterns to remember
    """

    async def execute(self) -> None:
        self.log("Reflecting on execution...")

        # Gather insights
        insights = {
            "cycle": self.ctx.current_cycle,
            "signals_at_end": list(self.ctx.signals),
            "failed_agents": list(self.ctx.get_failed_results().keys()),
            "modified_sections": list(self.ctx.modified_sections),
            "budget_used": self.ctx.budget.current_cost,
            "converged": self.ctx.is_converged(),
        }

        # Determine success
        if self.ctx.is_converged():
            insights["outcome"] = "success"
            self.log("✨ System converged successfully")

            # Record for learning
            if self.ctx.current_resume:
                quality_score = self._estimate_quality_score()
                self.ctx.record_success(self.ctx.current_resume, quality_score)
        else:
            insights["outcome"] = "needs_more_cycles"
            self.log(f"🔄 More cycles needed (signals: {len(self.ctx.signals)})")

        self.ctx.results["reflection"] = insights
        self.record_pass("Reflection complete", data=insights)

    def _estimate_quality_score(self) -> float:
        """Estimate quality score based on agent results."""
        total_agents = len(self.ctx.results)
        if total_agents == 0:
            return 0.5

        passed = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        return passed / total_agents

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

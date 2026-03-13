"""[SSOT] Logic Node for Skill Extraction and Analysis.
Extracted from engines to comply with Blueprint Depth-2 Structure.
This is a deterministic utility, NOT an autonomous agent.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SkillGapResult:
    """Result of skill gap analysis."""

    missing_skills: list[str]
    existing_skills: list[str]
    gap_severity: str
    gap_score: float


@dataclass
class SkillExtractionResult:
    """Result of skill extraction from text."""

    technical_skills: list[str]
    soft_skills: list[str]
    domain_skills: list[str]
    tool_skills: list[str]
    confidence_score: float
    source_text_length: int


@dataclass
class SkillMatchResult:
    """Result of skill matching between candidate and job requirements."""

    matched_skills: list[str]
    partially_matched_skills: list[str]
    unmatched_skills: list[str]
    match_percentage: float
    skill_categories: dict[str, dict[str, list[str]]]


@dataclass
class SkillAnalysisOutput:
    """Complete skill analysis output."""

    extraction_result: SkillExtractionResult
    gap_result: SkillGapResult
    match_result: SkillMatchResult
    recommendations: list[str]
    metadata: dict[str, Any]


class SkillExtractorNode:
    """
    Handles skill extraction, gap analysis, and matching for resume generation.

    This is a deterministic logic node that extracts and analyzes skills from
    job descriptions and candidate profiles. It is NOT an autonomous agent.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.technical_skills = {
            "programming": [
                "python",
                "java",
                "javascript",
                "typescript",
                "c++",
                "c#",
                "go",
                "rust",
                "ruby",
                "php",
                "swift",
                "kotlin",
                "scala",
                "perl",
                "r",
                "matlab",
            ],
            "web_development": [
                "html",
                "css",
                "react",
                "angular",
                "vue",
                "node.js",
                "express",
                "django",
                "flask",
                "spring",
                "laravel",
                "rails",
                "asp.net",
                "next.js",
                "gatsby",
            ],
            "databases": [
                "sql",
                "mysql",
                "postgresql",
                "mongodb",
                "redis",
                "elasticsearch",
                "oracle",
                "sql server",
                "cassandra",
                "dynamodb",
                "firebase",
            ],
            "cloud": [
                "aws",
                "azure",
                "gcp",
                "google cloud",
                "heroku",
                "digitalocean",
                "terraform",
                "kubernetes",
                "docker",
                "jenkins",
                "ci/cd",
                "devops",
            ],
            "data_science": [
                "machine learning",
                "data analysis",
                "statistics",
                "pandas",
                "numpy",
                "scikit-learn",
                "tensorflow",
                "pytorch",
                "tableau",
                "power bi",
                "excel",
            ],
        }
        self.soft_skills = [
            "leadership",
            "communication",
            "teamwork",
            "problem solving",
            "critical thinking",
            "adaptability",
            "time management",
            "project management",
            "creativity",
            "collaboration",
            "attention to detail",
            "analytical thinking",
            "strategic planning",
            "decision making",
            "mentoring",
            "public speaking",
            "negotiation",
            "conflict resolution",
            "emotional intelligence",
        ]
        self.domain_skills = {
            "finance": [
                "financial analysis",
                "investment banking",
                "risk management",
                "portfolio management",
                "financial modeling",
                "compliance",
                "audit",
                "tax planning",
                "mergers and acquisitions",
            ],
            "healthcare": [
                "clinical research",
                "medical terminology",
                "patient care",
                "healthcare compliance",
                "medical coding",
                "pharmacology",
                "healthcare informatics",
                "clinical trials",
            ],
            "technology": [
                "software development",
                "system architecture",
                "api design",
                "microservices",
                "agile methodology",
                "scrum",
                "code review",
                "testing",
                "debugging",
                "optimization",
            ],
            "marketing": [
                "digital marketing",
                "seo",
                "sem",
                "content marketing",
                "social media marketing",
                "brand management",
                "market research",
                "analytics",
                "copywriting",
                "campaign management",
            ],
        }
        self.tool_skills = {
            "development_tools": [
                "git",
                "github",
                "gitlab",
                "jira",
                "confluence",
                "slack",
                "vs code",
                "intellij",
                "eclipse",
                "postman",
                "docker",
                "kubernetes",
                "terraform",
                "ansible",
            ],
            "design_tools": [
                "figma",
                "sketch",
                "adobe creative suite",
                "photoshop",
                "illustrator",
                "xd",
                "invision",
                "zeplin",
                "canva",
                "gimp",
            ],
            "office_tools": [
                "microsoft office",
                "word",
                "excel",
                "powerpoint",
                "outlook",
                "google workspace",
                "docs",
                "sheets",
                "slides",
                "notion",
                "trello",
                "asana",
            ],
        }
        # guardian: allow-magic-config
        self.exact_match_threshold = 0.9
        # guardian: allow-magic-config
        self.partial_match_threshold = 0.7

    def __call__(self, job_description: str, candidate_profile: dict[str, Any] = None) -> SkillAnalysisOutput:
        """
        Executes skill analysis using functor pattern.

        Args:
            job_description: Job description text
            candidate_profile: Candidate's current profile/resume data

        Returns:
            SkillAnalysisOutput: Complete skill analysis
        """
        if not job_description:
            raise ValueError("Job description cannot be empty")
        return self.analyze_skills(job_description, candidate_profile or {})

    def analyze_skills(self, job_description: str, candidate_profile: dict[str, Any]) -> SkillAnalysisOutput:
        """Analyze skills from job description and candidate profile.

        Args:
            job_description: Job description text
            candidate_profile: Candidate's profile data

        Returns:
            SkillAnalysisOutput with extraction, gap, and match analysis
        """
        logger.info("Analyzing skills from job description and candidate profile")
        jd_skills = self._extract_skills_from_text(job_description)
        logger.info(
            f"Extracted {len(jd_skills.technical_skills) + len(jd_skills.soft_skills)} skills from job description"
        )
        candidate_skills = self._extract_skills_from_profile(candidate_profile)
        logger.info(
            f"Extracted {len(candidate_skills.technical_skills) + len(candidate_skills.soft_skills)} skills from candidate profile"
        )
        gap_result = self._analyze_skill_gaps(jd_skills, candidate_skills)
        logger.info(f"Skill gap analysis: {gap_result.gap_severity} severity ({gap_result.gap_score:.2f})")
        match_result = self._match_skills(jd_skills, candidate_skills)
        logger.info(f"Skill matching: {match_result.match_percentage:.1f}% match")
        recommendations = self._generate_recommendations(gap_result, match_result)
        logger.info(f"Generated {len(recommendations)} recommendations")
        output = SkillAnalysisOutput(
            extraction_result=jd_skills,
            gap_result=gap_result,
            match_result=match_result,
            recommendations=recommendations,
            metadata={
                "node_id": "SkillExtractorNode",
                "job_description_length": len(job_description),
                "candidate_has_profile": bool(candidate_profile),
                "analysis_timestamp": self._get_timestamp(),
            },
        )
        logger.info(f"Skill analysis complete: {match_result.match_percentage:.1f}% match")
        return output

    def _extract_skills_from_text(self, text: str) -> SkillExtractionResult:
        """Extract skills from text using keyword matching and patterns.

        Args:
            text: Text to extract skills from

        Returns:
            SkillExtractionResult with categorized skills
        """
        text_lower = text.lower()
        technical_skills = []
        for _category, skills in self.technical_skills.items():
            for skill in skills:
                if skill in text_lower:
                    technical_skills.append(skill.title())
        soft_skills = []
        for skill in self.soft_skills:
            if skill in text_lower:
                soft_skills.append(skill.title())
        domain_skills = []
        for _industry, skills in self.domain_skills.items():
            for skill in skills:
                if skill in text_lower:
                    domain_skills.append(skill.title())
        tool_skills = []
        for _category, tools in self.tool_skills.items():
            for tool in tools:
                if tool in text_lower:
                    tool_skills.append(tool.title())
        total_skills = len(technical_skills) + len(soft_skills) + len(domain_skills) + len(tool_skills)
        confidence_score = min(0.95, 0.5 + total_skills * 0.02)
        return SkillExtractionResult(
            technical_skills=list(set(technical_skills)),
            soft_skills=list(set(soft_skills)),
            domain_skills=list(set(domain_skills)),
            tool_skills=list(set(tool_skills)),
            confidence_score=confidence_score,
            source_text_length=len(text),
        )

    def _extract_skills_from_profile(self, profile: dict[str, Any]) -> SkillExtractionResult:
        """Extract skills from candidate profile.

        Args:
            profile: Candidate profile data

        Returns:
            SkillExtractionResult with extracted skills
        """
        profile_text = ""
        for exp in profile.get("experience", []):
            profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
            for bullet in exp.get("bullets", []):
                profile_text += f" {bullet}"
        skills_section = profile.get("skills", [])
        if isinstance(skills_section, list):
            profile_text += " " + " ".join(str(s) for s in skills_section)
        else:
            profile_text += f" {skills_section}"
        profile_text += f" {profile.get('summary', '')}"
        for edu in profile.get("education", []):
            profile_text += f" {edu.get('degree', '')} {edu.get('field', '')}"
        return self._extract_skills_from_text(profile_text)

    def _analyze_skill_gaps(
        self, jd_skills: SkillExtractionResult, candidate_skills: SkillExtractionResult
    ) -> SkillGapResult:
        """Analyze skill gaps between job requirements and candidate profile.

        Args:
            jd_skills: Skills extracted from job description
            candidate_skills: Skills extracted from candidate profile

        Returns:
            SkillGapResult with gap analysis
        """
        jd_all_skills = set(
            jd_skills.technical_skills
            + jd_skills.soft_skills
            + jd_skills.domain_skills
            + jd_skills.tool_skills
        )
        candidate_all_skills = set(
            candidate_skills.technical_skills
            + candidate_skills.soft_skills
            + candidate_skills.domain_skills
            + candidate_skills.tool_skills
        )
        missing_skills = list(jd_all_skills - candidate_all_skills)
        existing_skills = list(candidate_all_skills & jd_all_skills)
        if len(jd_all_skills) == 0:
            gap_score = 0.0
            gap_severity = "LOW"
        else:
            gap_score = len(missing_skills) / len(jd_all_skills)
            if gap_score >= 0.7:
                gap_severity = "CRITICAL"
            elif gap_score >= 0.5:
                gap_severity = "HIGH"
            elif gap_score >= 0.3:
                gap_severity = "MEDIUM"
            else:
                gap_severity = "LOW"
        return SkillGapResult(
            missing_skills=sorted(missing_skills),
            existing_skills=sorted(existing_skills),
            gap_severity=gap_severity,
            gap_score=gap_score,
        )

    def _match_skills(
        self, jd_skills: SkillExtractionResult, candidate_skills: SkillExtractionResult
    ) -> SkillMatchResult:
        """Perform detailed skill matching between JD and candidate.

        Args:
            jd_skills: Skills from job description
            candidate_skills: Skills from candidate profile

        Returns:
            SkillMatchResult with detailed matching
        """
        jd_technical_set = {skill.lower() for skill in jd_skills.technical_skills}
        candidate_technical_set = {skill.lower() for skill in candidate_skills.technical_skills}
        matched_technical = list(jd_technical_set & candidate_technical_set)
        jd_soft_set = {skill.lower() for skill in jd_skills.soft_skills}
        candidate_soft_set = {skill.lower() for skill in candidate_skills.soft_skills}
        matched_soft = list(jd_soft_set & candidate_soft_set)
        jd_domain_set = {skill.lower() for skill in jd_skills.domain_skills}
        candidate_domain_set = {skill.lower() for skill in candidate_skills.domain_skills}
        matched_domain = list(jd_domain_set & candidate_domain_set)
        jd_tool_set = {skill.lower() for skill in jd_skills.tool_skills}
        candidate_tool_set = {skill.lower() for skill in candidate_skills.tool_skills}
        matched_tool = list(jd_tool_set & candidate_tool_set)
        all_matched_skills = matched_technical + matched_soft + matched_domain + matched_tool
        all_jd_skills = (
            jd_skills.technical_skills
            + jd_skills.soft_skills
            + jd_skills.domain_skills
            + jd_skills.tool_skills
        )
        [skill.lower() for skill in all_jd_skills]
        unmatched_skills = [skill for skill in all_jd_skills if skill.lower() not in all_matched_skills]
        total_jd_skills = len(all_jd_skills)
        match_percentage = len(all_matched_skills) / total_jd_skills if total_jd_skills > 0 else 0.0
        return SkillMatchResult(
            matched_skills=[skill.title() for skill in all_matched_skills],
            partially_matched_skills=[],
            unmatched_skills=unmatched_skills,
            match_percentage=match_percentage,
            skill_categories={
                "technical": {"matched": [skill.title() for skill in matched_technical]},
                "soft": {"matched": [skill.title() for skill in matched_soft]},
                "domain": {"matched": [skill.title() for skill in matched_domain]},
                "tools": {"matched": [skill.title() for skill in matched_tool]},
            },
        )

    def _generate_recommendations(
        self, gap_result: SkillGapResult, match_result: SkillMatchResult
    ) -> list[str]:
        """Generate recommendations based on skill analysis.

        Args:
            gap_result: Skill gap analysis result
            match_result: Skill matching result

        Returns:
            List of recommendations
        """
        recommendations = []
        if gap_result.gap_severity in ["HIGH", "CRITICAL"]:
            recommendations.append(f"Critical skill gaps identified ({gap_result.gap_severity} severity)")
            recommendations.append(f"Focus on acquiring: {', '.join(gap_result.missing_skills[:5])}")
        if match_result.match_percentage < 0.5:
            recommendations.append("Consider highlighting transferable skills more prominently")
        elif match_result.match_percentage > 0.8:
            recommendations.append("Strong skill alignment - emphasize relevant experience")
        if not match_result.skill_categories["technical"]["matched"]:
            recommendations.append("Add technical skills section to highlight relevant technologies")
        if not match_result.skill_categories["soft"]["matched"]:
            recommendations.append("Include soft skills that demonstrate leadership and collaboration")
        if len(gap_result.missing_skills) > 10:
            recommendations.append("Consider targeting roles that better align with current skillset")
        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_skill_categories(self) -> dict[str, list[str]]:
        """Get all available skill categories and their skills.

        Returns:
            Dictionary of skill categories and their associated skills
        """
        return {
            "technical": [skill for skills in self.technical_skills.values() for skill in skills],
            "soft": self.soft_skills.copy(),
            "domain": [skill for skills in self.domain_skills.values() for skill in skills],
            "tools": [skill for tools in self.tool_skills.values() for skill in tools],
        }

    def validate_skill_extraction(self, text: str, expected_skills: list[str]) -> dict[str, Any]:
        """Validate skill extraction against expected skills.

        Args:
            text: Text to extract skills from
            expected_skills: Expected skills to find

        Returns:
            Validation result with precision, recall, and f1 score
        """
        extraction_result = self._extract_skills_from_text(text)
        extracted_skills = set(
            extraction_result.technical_skills
            + extraction_result.soft_skills
            + extraction_result.domain_skills
            + extraction_result.tool_skills
        )
        expected_skills_set = {skill.lower() for skill in expected_skills}
        true_positives = len(extracted_skills & expected_skills_set)
        false_positives = len(extracted_skills - expected_skills_set)
        false_negatives = len(expected_skills_set - extracted_skills)
        precision = (
            true_positives / (true_positives + false_positives)
            if true_positives + false_positives > 0
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if true_positives + false_negatives > 0
            else 0.0
        )
        f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0.0
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "extracted_skills": list(extracted_skills),
            "missing_expected": list(expected_skills_set - extracted_skills),
        }

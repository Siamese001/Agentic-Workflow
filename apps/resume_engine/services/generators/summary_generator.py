"""
Summary Generator Service
LEVEL 5 - Professional summary and objective generation
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import re

@dataclass
class SummaryResult:
    """Generated professional summary with metadata"""
    content: str
    word_count: int
    tone: str
    focus_areas: List[str]
    impact_score: float

class SummaryGenerator:
    """Generates compelling professional summaries tailored to job requirements"""

    def __init__(self):
        self.summary_templates = {
            "professional": [
                "Results-oriented {professionals} with {years} years of experience in {industries}",
                "Skilled {professionals} specializing in {skills} with proven track record",
                "Accomplished {professionals} with expertise in {skills} and {achievements}"
            ],
            "career_change": [
                "Dynamic professional transitioning from {background} to {target_field}",
                "Versatile {professionals} leveraging transferable skills in {skills}",
                "Adaptable {professionals} with strong foundation in {background} and passion for {target_field}"
            ],
            "senior_level": [
                "Seasoned {professionals} with {years}+ years leading {teams} and driving {results}",
                "Strategic {professionals} with extensive experience in {industries} and {skills}",
                "Executive-level {professionals} with proven success in {achievements} and {leadership}"
            ]
        }

        self.impact_keywords = [
            "increased", "decreased", "improved", "enhanced", "optimized",
            "reduced", "achieved", "delivered", "generated", "saved"
        ]

    async def generate_summary(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> SummaryResult:
        """
        Generate a tailored professional summary
        
        Args:
            user_profile: User's professional data and experience
            job_description: Target job requirements
            preferences: Summary style and focus preferences
            
        Returns:
            Generated summary with metadata
        """
        preferences = preferences or {}

        # Analyze user profile and job requirements
        profile_analysis = await self._analyze_profile(user_profile)
        job_analysis = await self._analyze_job_requirements(job_description)

        # Determine summary type and tone
        summary_type = await self._determine_summary_type(profile_analysis, job_analysis)
        tone = preferences.get("tone", "professional")

        # Generate core summary content
        summary_content = await self._generate_core_summary(
            profile_analysis, job_analysis, summary_type, tone
        )

        # Add impact and quantification
        enhanced_summary = await self._enhance_with_impact(summary_content, profile_analysis)

        # Calculate metrics
        word_count = len(enhanced_summary.split())
        focus_areas = await self._extract_focus_areas(enhanced_summary, job_analysis)
        impact_score = await self._calculate_impact_score(enhanced_summary)

        return SummaryResult(
            content=enhanced_summary,
            word_count=word_count,
            tone=tone,
            focus_areas=focus_areas,
            impact_score=impact_score
        )

    async def _analyze_profile(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile for key attributes"""
        analysis = {
            "years_experience": len(user_profile.get("experience", [])),
            "skills": user_profile.get("skills", []),
            "industries": [],
            "achievements": [],
            "career_level": "mid",
            "specializations": []
        }

        # Extract industries from experience
        for exp in user_profile.get("experience", []):
            company = exp.get("company", "")
            position = exp.get("position", "")
            # Simple industry extraction (could be enhanced with industry mapping)
            if "tech" in company.lower() or "software" in position.lower():
                analysis["industries"].append("technology")
            elif "finance" in company.lower() or "banking" in position.lower():
                analysis["industries"].append("finance")
            elif "health" in company.lower() or "medical" in position.lower():
                analysis["industries"].append("healthcare")

        # Extract achievements
        for exp in user_profile.get("experience", []):
            description = exp.get("description", "")
            if any(keyword in description.lower() for keyword in self.impact_keywords):
                analysis["achievements"].append(description)

        # Determine career level
        if analysis["years_experience"] >= 10:
            analysis["career_level"] = "senior"
        elif analysis["years_experience"] >= 5:
            analysis["career_level"] = "mid"
        else:
            analysis["career_level"] = "junior"

        # Identify specializations
        skills = analysis["skills"]
        if any(skill in skills for skill in ["python", "java", "javascript"]):
            analysis["specializations"].append("software_development")
        if any(skill in skills for skill in ["aws", "azure", "gcp"]):
            analysis["specializations"].append("cloud_computing")
        if any(skill in skills for skill in ["leadership", "management", "team"]):
            analysis["specializations"].append("management")

        return analysis

    async def _analyze_job_requirements(self, job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job requirements for key attributes"""
        analysis = {
            "required_skills": [],
            "required_experience": 0,
            "industry_focus": "",
            "key_responsibilities": [],
            "seniority_level": "mid"
        }

        # Extract required skills
        requirements = job_description.get("requirements", [])
        for req in requirements:
            words = re.findall(r'\b\w+\b', req.lower())
            analysis["required_skills"].extend([word for word in words if len(word) > 3])

        # Extract experience requirements
        title = job_description.get("title", "").lower()
        if "senior" in title or "lead" in title:
            analysis["seniority_level"] = "senior"
        elif "junior" in title or "entry" in title:
            analysis["seniority_level"] = "junior"

        # Extract key responsibilities
        responsibilities = job_description.get("responsibilities", [])
        analysis["key_responsibilities"] = responsibilities[:3]

        return analysis

    async def _determine_summary_type(
        self,
        profile_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> str:
        """Determine the best summary type based on profile and job"""
        profile_level = profile_analysis["career_level"]
        job_level = job_analysis["seniority_level"]

        if profile_level == "senior" or job_level == "senior":
            return "senior_level"
        elif profile_level != job_level:
            return "career_change"
        else:
            return "professional"

    async def _generate_core_summary(
        self,
        profile_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any],
        summary_type: str,
        tone: str
    ) -> str:
        """Generate the core summary content"""
        templates = self.summary_templates[summary_type]

        # Select template
        template = templates[0]  # Could add logic to select best template

        # Prepare template variables
        years = profile_analysis["years_experience"]
        skills = profile_analysis["skills"][:3]
        industries = list(set(profile_analysis["industries"])) or "various industries"

        # Build summary
        if summary_type == "professional":
            summary = template.format(
                professionals="professional",
                years=f"{years}" if years > 0 else "several",
                industries=industries,
                skills=", ".join(skills),
                achievements="delivering results"
            )

        elif summary_type == "senior_level":
            summary = template.format(
                professionals="leader",
                years=f"{years}",
                teams="cross-functional teams",
                results="organizational success",
                industries=industries,
                skills=", ".join(skills),
                achievements="strategic initiatives",
                leadership="team development"
            )

        else:  # career_change
            background = profile_analysis["industries"][0] if profile_analysis["industries"] else "current field"
            target_field = job_analysis["required_skills"][0] if job_analysis["required_skills"] else "new domain"

            summary = template.format(
                background=background,
                target_field=target_field,
                professionals="professional",
                skills=", ".join(skills)
            )

        # Add job-specific tailoring
        if job_analysis["key_responsibilities"]:
            key_resp = job_analysis["key_responsibilities"][0]
            summary += f" with expertise in {key_resp.lower()}"

        return summary

    async def _enhance_with_impact(
        self,
        summary: str,
        profile_analysis: Dict[str, Any]
    ) -> str:
        """Enhance summary with impact statements and quantification"""
        enhanced = summary

        # Add impact statement if achievements exist
        if profile_analysis["achievements"]:
            enhanced += ". Proven ability to drive results and exceed targets"

        # Add forward-looking statement
        enhanced += ". Seeking to leverage expertise in a challenging new role"

        return enhanced

    async def _extract_focus_areas(
        self,
        summary: str,
        job_analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract key focus areas from the summary"""
        focus_areas = []

        # Extract from job requirements
        for skill in job_analysis["required_skills"][:5]:
            if skill.lower() in summary.lower():
                focus_areas.append(skill)

        # Add default focus areas if none found
        if not focus_areas:
            focus_areas = ["professional expertise", "results orientation", "continuous improvement"]

        return focus_areas

    async def _calculate_impact_score(self, summary: str) -> float:
        """Calculate impact score based on strong language and quantification"""
        summary_lower = summary.lower()

        # Count impact keywords
        impact_count = sum(1 for keyword in self.impact_keywords if keyword in summary_lower)

        # Check for quantification
        has_numbers = bool(re.search(r'\d+', summary))
        has_metrics = any(metric in summary_lower for metric in ["percent", "%", "increased", "decreased", "improved"])

        # Calculate score
        base_score = 0.5
        impact_bonus = min(impact_count * 0.1, 0.3)
        quantification_bonus = 0.1 if has_numbers else 0
        metrics_bonus = 0.1 if has_metrics else 0

        total_score = base_score + impact_bonus + quantification_bonus + metrics_bonus

        return min(total_score, 1.0)

__all__ = ["SummaryGenerator", "SummaryResult"]

"""
Resume Builder Service
LEVEL 5 - Core resume construction and content organization
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResumeSection:
    """Represents a section of the resume"""
    title: str
    content: List[str]
    priority: int = 1
    word_count: int = 0

class ResumeBuilder:
    """Builds and structures resume content from user data and job requirements"""

    def __init__(self):
        self.section_templates = {
            "summary": "Professional summary highlighting key qualifications",
            "experience": "Work experience with achievements and responsibilities",
            "education": "Educational background and qualifications",
            "skills": "Technical and soft skills relevant to the position"
        }
        self.max_word_count = 500  # For one-page resume

    async def build_resume(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Build complete resume from user profile and job requirements
        
        Args:
            user_profile: User's professional data
            job_description: Target job information
            preferences: Formatting and content preferences
            
        Returns:
            Structured resume with all sections
        """
        preferences = preferences or {}

        # Build each section
        sections = {}

        # Professional Summary
        sections["summary"] = await self._build_summary(user_profile, job_description)

        # Work Experience
        sections["experience"] = await self._build_experience(user_profile, job_description)

        # Education
        sections["education"] = await self._build_education(user_profile)

        # Skills
        sections["skills"] = await self._build_skills(user_profile, job_description)

        # Optimize for length and ATS
        optimized_resume = await self._optimize_resume(sections, preferences)

        return {
            "content": optimized_resume,
            "metadata": {
                "word_count": self._calculate_word_count(optimized_resume),
                "sections_count": len(optimized_resume),
                "build_timestamp": datetime.utcnow().isoformat()
            }
        }

    async def _build_summary(self, user_profile: Dict[str, Any], job_description: Dict[str, Any]) -> ResumeSection:
        """Build professional summary section"""
        summary_points = []

        # Extract key skills and experience
        skills = user_profile.get("skills", [])
        experience = user_profile.get("experience", [])

        # Create summary based on job requirements
        job_title = job_description.get("title", "")
        job_requirements = job_description.get("requirements", [])

        summary_points.append(f"Experienced professional with expertise in {', '.join(skills[:3])}")

        if experience:
            years_exp = len(experience)
            summary_points.append(f"{years_exp}+ years of progressive experience in {job_title}")

        if job_requirements:
            relevant_skills = [skill for skill in skills if any(req.lower() in skill.lower() for req in job_requirements)]
            if relevant_skills:
                summary_points.append(f"Proficient in {', '.join(relevant_skills[:2])} aligning with job requirements")

        return ResumeSection(
            title="Professional Summary",
            content=summary_points,
            priority=1
        )

    async def _build_experience(self, user_profile: Dict[str, Any], job_description: Dict[str, Any]) -> ResumeSection:
        """Build work experience section"""
        experience = user_profile.get("experience", [])
        job_requirements = job_description.get("requirements", [])

        experience_points = []

        for exp in experience:
            company = exp.get("company", "")
            position = exp.get("position", "")
            duration = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"

            # Create achievement bullet points
            achievements = exp.get("description", "").split(".")
            achievements = [a.strip() for a in achievements if a.strip()]

            # Tailor to job requirements
            tailored_achievements = []
            for achievement in achievements:
                # Check if achievement relates to job requirements
                if any(req.lower() in achievement.lower() for req in job_requirements):
                    tailored_achievements.append(f"• {achievement}")
                elif len(tailored_achievements) < 3:  # Keep most relevant
                    tailored_achievements.append(f"• {achievement}")

            exp_entry = f"{position} - {company} ({duration})"
            experience_points.append(exp_entry)
            experience_points.extend(tailored_achievements)

        return ResumeSection(
            title="Professional Experience",
            content=experience_points,
            priority=2
        )

    async def _build_education(self, user_profile: Dict[str, Any]) -> ResumeSection:
        """Build education section"""
        education = user_profile.get("education", [])
        education_points = []

        for edu in education:
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            year = edu.get("graduation_year", "")

            edu_entry = f"{degree} - {institution} ({year})"
            education_points.append(edu_entry)

        return ResumeSection(
            title="Education",
            content=education_points,
            priority=3
        )

    async def _build_skills(self, user_profile: Dict[str, Any], job_description: Dict[str, Any]) -> ResumeSection:
        """Build skills section"""
        user_skills = user_profile.get("skills", [])
        job_requirements = job_description.get("requirements", [])

        # Categorize skills and prioritize based on job requirements
        technical_skills = []
        soft_skills = []

        for skill in user_skills:
            # Check if skill matches job requirements
            is_relevant = any(req.lower() in skill.lower() for req in job_requirements)

            if any(tech in skill.lower() for tech in ["python", "java", "sql", "aws", "docker"]):
                technical_skills.append((skill, is_relevant))
            else:
                soft_skills.append((skill, is_relevant))

        # Sort by relevance
        technical_skills.sort(key=lambda x: x[1], reverse=True)
        soft_skills.sort(key=lambda x: x[1], reverse=True)

        skills_points = []

        if technical_skills:
            skills_points.append("Technical Skills:")
            skills_points.extend([f"• {skill}" for skill, _ in technical_skills[:8]])

        if soft_skills:
            skills_points.append("Soft Skills:")
            skills_points.extend([f"• {skill}" for skill, _ in soft_skills[:5]])

        return ResumeSection(
            title="Skills & Expertise",
            content=skills_points,
            priority=4
        )

    async def _optimize_resume(self, sections: Dict[str, ResumeSection], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resume for length and ATS compliance"""
        format_type = preferences.get("format", "chronological")
        max_length = preferences.get("length", "one_page")

        # Sort sections by priority
        sorted_sections = sorted(sections.items(), key=lambda x: x[1].priority)

        optimized_content = {}

        for section_name, section in sorted_sections:
            # Truncate if needed for one-page format
            if max_length == "one_page" and self._calculate_word_count(optimized_content) > 400:
                # Keep only high-priority sections
                if section.priority <= 2:
                    optimized_content[section_name] = {
                        "title": section.title,
                        "content": section.content
                    }
            else:
                optimized_content[section_name] = {
                    "title": section.title,
                    "content": section.content
                }

        return optimized_content

    def _calculate_word_count(self, content: Dict[str, Any]) -> int:
        """Calculate total word count of resume content"""
        total_words = 0
        for section in content.values():
            if isinstance(section.get("content"), list):
                for item in section["content"]:
                    total_words += len(item.split())
            elif isinstance(section.get("content"), str):
                total_words += len(section["content"].split())
        return total_words

__all__ = ["ResumeBuilder", "ResumeSection"]

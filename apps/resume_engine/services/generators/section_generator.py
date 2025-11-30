"""
Section Generator Service
LEVEL 5 - Dynamic resume section content generation
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
import re

@dataclass
class SectionContent:
    """Generated section content with metadata"""
    title: str
    content: List[str]
    word_count: int
    relevance_score: float

class SectionGenerator:
    """Generates optimized content for different resume sections"""
    
    def __init__(self):
        self.section_templates = {
            "summary": {
                "max_words": 50,
                "structure": "skills + experience + goals",
                "tone": "professional"
            },
            "experience": {
                "max_words": 200,
                "structure": "achievements + responsibilities",
                "tone": "action-oriented"
            },
            "education": {
                "max_words": 80,
                "structure": "degree + institution + achievements",
                "tone": "academic"
            },
            "skills": {
                "max_words": 100,
                "structure": "technical + soft skills",
                "tone": "concise"
            }
        }
        
        self.action_verbs = [
            "developed", "implemented", "managed", "led", "optimized",
            "designed", "coordinated", "achieved", "improved", "enhanced",
            "created", "launched", "maintained", "supported", "analyzed"
        ]
    
    async def generate_section(
        self,
        section_type: str,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> SectionContent:
        """
        Generate optimized content for a specific resume section
        
        Args:
            section_type: Type of section to generate
            user_profile: User's professional data
            job_description: Target job requirements
            preferences: Content generation preferences
            
        Returns:
            Generated section content with metadata
        """
        preferences = preferences or {}
        
        if section_type == "summary":
            content = await self._generate_summary(user_profile, job_description, preferences)
        elif section_type == "experience":
            content = await self._generate_experience(user_profile, job_description, preferences)
        elif section_type == "education":
            content = await self._generate_education(user_profile, job_description, preferences)
        elif section_type == "skills":
            content = await self._generate_skills(user_profile, job_description, preferences)
        else:
            content = await self._generate_custom_section(section_type, user_profile, job_description, preferences)
        
        return content
    
    async def _generate_summary(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> SectionContent:
        """Generate professional summary section"""
        summary_points = []
        
        # Extract key information
        skills = user_profile.get("skills", [])[:5]  # Top 5 skills
        experience = user_profile.get("experience", [])
        job_title = job_description.get("title", "")
        job_requirements = job_description.get("requirements", [])
        
        # Generate opening statement
        years_experience = len(experience)
        if years_experience > 0:
            summary_points.append(f"Results-oriented professional with {years_experience}+ years of experience")
        
        # Highlight key skills relevant to job
        relevant_skills = [
            skill for skill in skills 
            if any(req.lower() in skill.lower() for req in job_requirements)
        ][:3]
        
        if relevant_skills:
            summary_points.append(f"Expertise in {', '.join(relevant_skills)}")
        
        # Add job-specific focus
        if job_title:
            summary_points.append(f"Specialized in {job_title} with proven track record of success")
        
        # Include achievement focus
        summary_points.append("Committed to delivering exceptional results and driving organizational growth")
        
        # Calculate metrics
        word_count = sum(len(point.split()) for point in summary_points)
        relevance_score = await self._calculate_relevance_score(summary_points, job_requirements)
        
        return SectionContent(
            title="Professional Summary",
            content=summary_points,
            word_count=word_count,
            relevance_score=relevance_score
        )
    
    async def _generate_experience(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> SectionContent:
        """Generate work experience section"""
        experience_points = []
        experience = user_profile.get("experience", [])
        job_requirements = job_description.get("requirements", [])
        
        for exp in experience:
            company = exp.get("company", "")
            position = exp.get("position", "")
            duration = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            
            # Position header
            experience_points.append(f"{position} - {company} ({duration})")
            
            # Generate achievement bullet points
            description = exp.get("description", "")
            achievements = await self._extract_achievements(description, job_requirements)
            
            for achievement in achievements[:4]:  # Max 4 bullet points per position
                experience_points.append(f"• {achievement}")
        
        # Calculate metrics
        word_count = sum(len(point.split()) for point in experience_points)
        relevance_score = await self._calculate_relevance_score(experience_points, job_requirements)
        
        return SectionContent(
            title="Professional Experience",
            content=experience_points,
            word_count=word_count,
            relevance_score=relevance_score
        )
    
    async def _generate_education(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> SectionContent:
        """Generate education section"""
        education_points = []
        education = user_profile.get("education", [])
        
        for edu in education:
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            year = edu.get("graduation_year", "")
            gpa = edu.get("gpa", "")
            
            edu_line = f"{degree} - {institution}"
            if year:
                edu_line += f" ({year})"
            if gpa:
                edu_line += f" - GPA: {gpa}"
            
            education_points.append(edu_line)
        
        # Add relevant achievements if available
        for edu in education:
            achievements = edu.get("achievements", [])
            for achievement in achievements[:2]:  # Max 2 achievements per education
                education_points.append(f"• {achievement}")
        
        # Calculate metrics
        word_count = sum(len(point.split()) for point in education_points)
        relevance_score = 0.8  # Education is generally relevant
        
        return SectionContent(
            title="Education",
            content=education_points,
            word_count=word_count,
            relevance_score=relevance_score
        )
    
    async def _generate_skills(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> SectionContent:
        """Generate skills section"""
        skills_points = []
        skills = user_profile.get("skills", [])
        job_requirements = job_description.get("requirements", [])
        
        # Categorize skills
        technical_skills = []
        soft_skills = []
        
        for skill in skills:
            if any(tech in skill.lower() for tech in ["python", "java", "sql", "aws", "docker", "javascript"]):
                technical_skills.append(skill)
            else:
                soft_skills.append(skill)
        
        # Prioritize based on job requirements
        relevant_technical = [
            skill for skill in technical_skills
            if any(req.lower() in skill.lower() for req in job_requirements)
        ]
        other_technical = [skill for skill in technical_skills if skill not in relevant_technical]
        
        relevant_soft = [
            skill for skill in soft_skills
            if any(req.lower() in skill.lower() for req in job_requirements)
        ]
        other_soft = [skill for skill in soft_skills if skill not in relevant_soft]
        
        # Build skills section
        if relevant_technical or other_technical:
            skills_points.append("Technical Skills:")
            skills_points.extend([f"• {skill}" for skill in relevant_technical + other_technical[:8]])
        
        if relevant_soft or other_soft:
            skills_points.append("Soft Skills:")
            skills_points.extend([f"• {skill}" for skill in relevant_soft + other_soft[:5]])
        
        # Calculate metrics
        word_count = sum(len(point.split()) for point in skills_points)
        relevance_score = await self._calculate_relevance_score(skills_points, job_requirements)
        
        return SectionContent(
            title="Skills & Expertise",
            content=skills_points,
            word_count=word_count,
            relevance_score=relevance_score
        )
    
    async def _generate_custom_section(
        self,
        section_type: str,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> SectionContent:
        """Generate custom section based on type"""
        content_points = []
        
        if section_type == "certifications":
            certifications = user_profile.get("certifications", [])
            for cert in certifications:
                content_points.append(f"• {cert}")
        
        elif section_type == "projects":
            projects = user_profile.get("projects", [])
            for project in projects[:5]:
                content_points.append(f"• {project}")
        
        elif section_type == "languages":
            languages = user_profile.get("languages", [])
            for lang in languages:
                content_points.append(f"• {lang}")
        
        else:
            content_points.append(f"Custom {section_type} section content")
        
        word_count = sum(len(point.split()) for point in content_points)
        
        return SectionContent(
            title=section_type.replace("_", " ").title(),
            content=content_points,
            word_count=word_count,
            relevance_score=0.7
        )
    
    async def _extract_achievements(
        self,
        description: str,
        job_requirements: List[str]
    ) -> List[str]:
        """Extract and optimize achievement statements"""
        # Split description into sentences
        sentences = re.split(r'[.!?]+', description)
        achievements = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Start with action verb if not already
            words = sentence.split()
            if words and words[0].lower() not in self.action_verbs:
                # Try to infer appropriate action verb
                if any(word in sentence.lower() for word in ["develop", "create", "build"]):
                    sentence = "Developed " + sentence
                elif any(word in sentence.lower() for word in ["manage", "lead", "coordinate"]):
                    sentence = "Managed " + sentence
                elif any(word in sentence.lower() for word in ["improve", "optimize", "enhance"]):
                    sentence = "Improved " + sentence
                else:
                    sentence = "Handled " + sentence
            
            # Check relevance to job requirements
            is_relevant = any(req.lower() in sentence.lower() for req in job_requirements)
            
            if is_relevant or len(achievements) < 3:  # Keep most relevant
                achievements.append(sentence)
        
        return achievements[:4]  # Max 4 achievements
    
    async def _calculate_relevance_score(
        self,
        content: List[str],
        job_requirements: List[str]
    ) -> float:
        """Calculate relevance score based on job requirements"""
        if not job_requirements:
            return 0.5
        
        content_text = " ".join(content).lower()
        matches = 0
        
        for requirement in job_requirements:
            if any(word in content_text for word in requirement.lower().split() if len(word) > 2):
                matches += 1
        
        return matches / len(job_requirements)

__all__ = ["SectionGenerator", "SectionContent"]

"""
Unit Tests for Resume Builder
LEVEL 5 - Unit tests for resume builder service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from ...services.builders.resume_builder import ResumeBuilder, ResumeSection

class TestResumeBuilder:
    """Unit tests for ResumeBuilder class"""
    
    @pytest.fixture
    def resume_builder(self):
        """Create ResumeBuilder instance for testing"""
        return ResumeBuilder()
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing"""
        return {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer",
                    "start_date": "2020-01",
                    "end_date": "2023-01",
                    "description": "Developed web applications and led team projects."
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "Bachelor of Science",
                    "graduation_year": 2019
                }
            ],
            "skills": ["Python", "JavaScript", "SQL", "AWS", "Docker"]
        }
    
    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing"""
        return {
            "title": "Senior Software Engineer",
            "company": "Innovation Inc",
            "requirements": [
                "5+ years of software development experience",
                "Proficiency in Python and cloud technologies",
                "Strong leadership and communication skills"
            ],
            "responsibilities": [
                "Develop and maintain scalable software solutions",
                "Lead cross-functional development teams",
                "Mentor junior developers"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_build_resume_basic(self, resume_builder, sample_user_profile, sample_job_description):
        """Test basic resume building functionality"""
        result = await resume_builder.build_resume(sample_user_profile, sample_job_description)
        
        assert result is not None
        assert "content" in result
        assert "metadata" in result
        
        content = result["content"]
        assert len(content) > 0
        
        # Check required sections
        assert any("summary" in section.lower() for section in content.keys())
        assert any("experience" in section.lower() for section in content.keys())
        assert any("education" in section.lower() for section in content.keys())
        assert any("skill" in section.lower() for section in content.keys())
    
    @pytest.mark.asyncio
    async def test_build_summary_section(self, resume_builder, sample_user_profile, sample_job_description):
        """Test summary section generation"""
        summary = await resume_builder._build_summary(sample_user_profile, sample_job_description)
        
        assert isinstance(summary, ResumeSection)
        assert summary.title == "Professional Summary"
        assert len(summary.content) > 0
        assert summary.priority == 1
        assert summary.word_count >= 0
    
    @pytest.mark.asyncio
    async def test_build_experience_section(self, resume_builder, sample_user_profile, sample_job_description):
        """Test experience section generation"""
        experience = await resume_builder._build_experience(sample_user_profile, sample_job_description)
        
        assert isinstance(experience, ResumeSection)
        assert experience.title == "Professional Experience"
        assert len(experience.content) > 0
        assert experience.priority == 2
        
        # Check that company and position are included
        content_text = " ".join(experience.content).lower()
        assert "tech corp" in content_text
        assert "software engineer" in content_text
    
    @pytest.mark.asyncio
    async def test_build_education_section(self, resume_builder, sample_user_profile, sample_job_description):
        """Test education section generation"""
        education = await resume_builder._build_education(sample_user_profile)
        
        assert isinstance(education, ResumeSection)
        assert education.title == "Education"
        assert len(education.content) > 0
        assert education.priority == 3
        
        # Check that institution and degree are included
        content_text = " ".join(education.content).lower()
        assert "university" in content_text
        assert "bachelor of science" in content_text
    
    @pytest.mark.asyncio
    async def test_build_skills_section(self, resume_builder, sample_user_profile, sample_job_description):
        """Test skills section generation"""
        skills = await resume_builder._build_skills(sample_user_profile, sample_job_description)
        
        assert isinstance(skills, ResumeSection)
        assert skills.title == "Skills & Expertise"
        assert len(skills.content) > 0
        assert skills.priority == 4
        
        # Check that user skills are included
        content_text = " ".join(skills.content).lower()
        assert "python" in content_text
        assert "javascript" in content_text
    
    @pytest.mark.asyncio
    async def test_optimize_resume_chronological(self, resume_builder, sample_user_profile, sample_job_description):
        """Test resume optimization for chronological format"""
        sections = {
            "summary": ResumeSection("Summary", ["Test summary"], 10),
            "experience": ResumeSection("Experience", ["Test experience"], 20),
            "education": ResumeSection("Education", ["Test education"], 5),
            "skills": ResumeSection("Skills", ["Test skills"], 15)
        }
        
        preferences = {"format": "chronological", "length": "one_page"}
        optimized = await resume_builder._optimize_resume(sections, preferences)
        
        assert optimized is not None
        assert len(optimized) > 0
        
        # Check that sections are ordered correctly
        section_order = list(optimized.keys())
        experience_index = section_order.index("experience") if "experience" in section_order else -1
        education_index = section_order.index("education") if "education" in section_order else -1
        
        # In chronological format, experience should come before education
        if experience_index >= 0 and education_index >= 0:
            assert experience_index < education_index
    
    @pytest.mark.asyncio
    async def test_calculate_word_count(self, resume_builder):
        """Test word count calculation"""
        content = {
            "section1": {
                "content": ["This is a test sentence with five words.", "Another sentence here."]
            },
            "section2": {
                "content": "Single line content with six words total."
            }
        }
        
        word_count = resume_builder._calculate_word_count(content)
        assert word_count == 11  # 5 + 5 + 6
    
    @pytest.mark.asyncio
    async def test_build_resume_with_preferences(self, resume_builder, sample_user_profile, sample_job_description):
        """Test resume building with custom preferences"""
        preferences = {
            "format": "functional",
            "tone": "casual",
            "length": "two_pages"
        }
        
        result = await resume_builder.build_resume(sample_user_profile, sample_job_description, preferences)
        
        assert result is not None
        assert "content" in result
        assert "metadata" in result
        
        # Check that preferences were considered
        metadata = result["metadata"]
        assert "build_timestamp" in metadata
    
    @pytest.mark.asyncio
    async def test_build_resume_empty_profile(self, resume_builder, sample_job_description):
        """Test resume building with empty user profile"""
        empty_profile = {
            "name": "",
            "experience": [],
            "education": [],
            "skills": []
        }
        
        result = await resume_builder.build_resume(empty_profile, sample_job_description)
        
        # Should still generate a basic structure
        assert result is not None
        assert "content" in result
        assert len(result["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_build_resume_empty_job_description(self, resume_builder, sample_user_profile):
        """Test resume building with empty job description"""
        empty_job = {
            "title": "",
            "company": "",
            "requirements": [],
            "responsibilities": []
        }
        
        result = await resume_builder.build_resume(sample_user_profile, empty_job)
        
        # Should still generate a basic structure
        assert result is not None
        assert "content" in result
        assert len(result["content"]) > 0
    
    def test_resume_section_creation(self):
        """Test ResumeSection dataclass creation"""
        section = ResumeSection(
            title="Test Section",
            content=["Point 1", "Point 2", "Point 3"],
            priority=1,
            word_count=10
        )
        
        assert section.title == "Test Section"
        assert len(section.content) == 3
        assert section.priority == 1
        assert section.word_count == 10
    
    @pytest.mark.asyncio
    async def test_extract_achievements(self, resume_builder):
        """Test achievement extraction from descriptions"""
        description = "Developed new features that improved performance by 30%. Led team of 5 developers."
        job_requirements = ["performance improvement", "leadership"]
        
        achievements = await resume_builder._extract_achievements(description, job_requirements)
        
        assert len(achievements) > 0
        assert any("improved" in achievement.lower() for achievement in achievements)
        assert any("led" in achievement.lower() for achievement in achievements)

if __name__ == "__main__":
    pytest.main([__file__])

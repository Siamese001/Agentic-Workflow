"""
Unit Tests for Skill Expander
LEVEL 5 - Unit tests for skill expander service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from ...services.enrichers.skill_expander import SkillExpander, SkillAnalysis

class TestSkillExpander:
    """Unit tests for SkillExpander class"""
    
    @pytest.fixture
    def skill_expander(self):
        """Create SkillExpander instance for testing"""
        return SkillExpander()
    
    @pytest.fixture
    def sample_user_skills(self):
        """Sample user skills for testing"""
        return ["Python", "JavaScript", "SQL", "AWS", "Docker", "Leadership", "Communication"]
    
    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing"""
        return {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "requirements": [
                "Strong Python programming skills",
                "Experience with cloud platforms like AWS",
                "Docker containerization knowledge",
                "Leadership and team management abilities"
            ],
            "responsibilities": [
                "Develop scalable applications using Python",
                "Lead development teams",
                "Deploy and manage cloud infrastructure"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_expand_skills_basic(self, skill_expander, sample_user_skills, sample_job_description):
        """Test basic skill expansion functionality"""
        result = await skill_expander.expand_skills(sample_user_skills, sample_job_description)
        
        assert isinstance(result, SkillAnalysis)
        assert len(result.expanded_skills) > 0
        assert isinstance(result.skill_categories, dict)
        assert isinstance(result.proficiency_levels, dict)
        assert isinstance(result.recommended_additions, list)
    
    @pytest.mark.asyncio
    async def test_normalize_skills(self, skill_expander):
        """Test skill normalization"""
        skills = ["python", "JS", "py", "SQL", "Docker", "  Leadership  ", ""]
        
        normalized = await skill_expander._normalize_skills(skills)
        
        assert "python" in normalized
        assert "javascript" in normalized  # JS should be expanded
        assert "sql" in normalized
        assert "docker" in normalized
        assert "leadership" in normalized
        assert "" not in normalized  # Empty string should be removed
    
    @pytest.mark.asyncio
    async def test_categorize_skills(self, skill_expander):
        """Test skill categorization"""
        skills = ["python", "javascript", "aws", "docker", "leadership", "communication"]
        
        categories = await skill_expander._categorize_skills(skills)
        
        assert isinstance(categories, dict)
        assert "programming_languages" in categories
        assert "cloud_platforms" in categories
        assert "soft_skills" in categories
        
        # Check specific categorizations
        assert "python" in categories["programming_languages"]
        assert "javascript" in categories["programming_languages"]
        assert "aws" in categories["cloud_platforms"]
        assert "leadership" in categories["soft_skills"]
    
    @pytest.mark.asyncio
    async def test_extract_skill_requirements(self, skill_expander, sample_job_description):
        """Test skill requirement extraction from job description"""
        requirements = await skill_expander._extract_skill_requirements(sample_job_description)
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        
        # Check that relevant skills are extracted
        req_text = " ".join(requirements).lower()
        assert "python" in req_text
        assert "aws" in req_text
        assert "docker" in req_text
        assert "leadership" in req_text
    
    @pytest.mark.asyncio
    async def test_expand_based_on_requirements(self, skill_expander):
        """Test skill expansion based on job requirements"""
        user_skills = ["python", "javascript"]
        job_requirements = ["python", "aws", "docker", "leadership"]
        
        expanded = await skill_expander._expand_based_on_requirements(user_skills, job_requirements)
        
        assert isinstance(expanded, list)
        assert "python" in expanded  # Original skill should be preserved
        assert "javascript" in expanded  # Original skill should be preserved
        
        # Should include related skills for matching requirements
        expanded_text = " ".join(expanded).lower()
        assert any(tech in expanded_text for tech in ["django", "flask", "fastapi"])  # Python-related
    
    @pytest.mark.asyncio
    async def test_estimate_proficiency_levels(self, skill_expander):
        """Test proficiency level estimation"""
        skills = ["python", "senior python developer", "basic javascript", "learning aws"]
        
        proficiency = await skill_expander._estimate_proficiency_levels(skills)
        
        assert isinstance(proficiency, dict)
        assert len(proficiency) == len(skills)
        
        # Check proficiency assignments
        assert proficiency["python"] == "intermediate"  # Default
        assert proficiency["senior python developer"] == "advanced"  # Senior keyword
        assert proficiency["basic javascript"] == "beginner"  # Basic keyword
        assert proficiency["learning aws"] == "beginner"  # Learning keyword
    
    @pytest.mark.asyncio
    async def test_generate_skill_recommendations(self, skill_expander):
        """Test skill recommendation generation"""
        current_skills = ["python", "javascript"]
        job_requirements = ["python", "aws", "docker", "kubernetes", "react"]
        
        recommendations = await skill_expander._generate_skill_recommendations(current_skills, job_requirements)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should recommend missing key skills
        rec_text = " ".join(recommendations).lower()
        assert any(req in rec_text for req in ["aws", "docker", "kubernetes", "react"])
    
    @pytest.mark.asyncio
    async def test_expand_skills_with_empty_inputs(self, skill_expander):
        """Test skill expansion with empty inputs"""
        result = await skill_expander.expand_skills([], {})
        
        assert isinstance(result, SkillAnalysis)
        assert len(result.expanded_skills) == 0
        assert len(result.skill_categories) == 0
        assert len(result.proficiency_levels) == 0
        assert len(result.recommended_additions) >= 0
    
    @pytest.mark.asyncio
    async def test_expand_skills_with_no_job_description(self, skill_expander, sample_user_skills):
        """Test skill expansion without job description"""
        result = await skill_expander.expand_skills(sample_user_skills, {})
        
        assert isinstance(result, SkillAnalysis)
        assert len(result.expanded_skills) > 0
        
        # Should still categorize skills even without job description
        assert len(result.skill_categories) > 0
    
    @pytest.mark.asyncio
    async def test_skill_analysis_dataclass(self):
        """Test SkillAnalysis dataclass creation"""
        analysis = SkillAnalysis(
            expanded_skills=["python", "javascript", "aws"],
            skill_categories={"programming_languages": ["python", "javascript"]},
            proficiency_levels={"python": "advanced", "javascript": "intermediate"},
            recommended_additions=["docker", "kubernetes"]
        )
        
        assert len(analysis.expanded_skills) == 3
        assert len(analysis.skill_categories) == 1
        assert len(analysis.proficiency_levels) == 2
        assert len(analysis.recommended_additions) == 2
    
    @pytest.mark.asyncio
    async def test_expand_skills_with_duplicates(self, skill_expander):
        """Test skill expansion with duplicate inputs"""
        skills_with_duplicates = ["python", "javascript", "python", "SQL", "sql", "AWS"]
        
        result = await skill_expander.expand_skills(skills_with_duplicates, {})
        
        assert isinstance(result, SkillAnalysis)
        # Should remove duplicates in expanded skills
        assert len(set(result.expanded_skills)) == len(result.expanded_skills)
    
    @pytest.mark.asyncio
    async def test_expand_skills_with_specialized_skills(self, skill_expander):
        """Test skill expansion with specialized technical skills"""
        specialized_skills = ["react", "vue", "angular", "node.js", "express", "typescript"]
        
        result = await skill_expander.expand_skills(specialized_skills, {})
        
        assert isinstance(result, SkillAnalysis)
        assert "javascript" in result.expanded_skills  # Should recognize JS framework relationship
        
        # Should categorize under programming_languages
        if "programming_languages" in result.skill_categories:
            programming_skills = result.skill_categories["programming_languages"]
            assert any("javascript" in skill.lower() or skill in specialized_skills for skill in programming_skills)

if __name__ == "__main__":
    pytest.main([__file__])

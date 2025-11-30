"""
Integration Tests for Resume Pipeline
LEVEL 5 - Integration tests for resume generation pipeline
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from datetime import datetime

from ...services.pipelines.resume_pipeline import ResumePipeline, PipelineResult
from ...services.builders.resume_builder import ResumeBuilder
from ...services.enrichers.skill_expander import SkillExpander
from ...services.generators.section_generator import SectionGenerator

class TestResumePipelineIntegration:
    """Integration tests for complete resume pipeline"""
    
    @pytest.fixture
    def resume_pipeline(self):
        """Create ResumePipeline instance for testing"""
        return ResumePipeline()
    
    @pytest.fixture
    def complete_request(self):
        """Complete resume generation request"""
        return {
            "user_profile": {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "555-0123",
                "experience": [
                    {
                        "company": "Tech Solutions Inc",
                        "position": "Senior Software Engineer",
                        "start_date": "2019-03",
                        "end_date": "2023-12",
                        "description": "Led development of cloud-native applications, improved system performance by 40%, and mentored team of 5 developers."
                    },
                    {
                        "company": "Digital Innovations",
                        "position": "Software Engineer",
                        "start_date": "2017-01",
                        "end_date": "2019-02",
                        "description": "Developed REST APIs and microservices, implemented CI/CD pipelines, and collaborated with cross-functional teams."
                    }
                ],
                "education": [
                    {
                        "institution": "State University",
                        "degree": "Master of Science in Computer Science",
                        "graduation_year": 2016
                    },
                    {
                        "institution": "Tech College",
                        "degree": "Bachelor of Science in Software Engineering",
                        "graduation_year": 2014
                    }
                ],
                "skills": [
                    "Python", "JavaScript", "TypeScript", "React", "Node.js",
                    "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
                    "Git", "CI/CD", "Agile", "Leadership", "Communication"
                ]
            },
            "job_description": {
                "title": "Principal Software Engineer",
                "company": "CloudTech Corporation",
                "requirements": [
                    "7+ years of software development experience",
                    "Expertise in cloud platforms (AWS preferred)",
                    "Strong background in microservices architecture",
                    "Experience with containerization (Docker, Kubernetes)",
                    "Leadership experience and team mentoring skills",
                    "Proficiency in modern JavaScript frameworks",
                    "Database design and optimization skills"
                ],
                "responsibilities": [
                    "Lead architectural decisions for cloud-native systems",
                    "Mentor and develop senior engineering team",
                    "Drive technical excellence and best practices",
                    "Collaborate with product and business stakeholders"
                ]
            }
        }
    
    @pytest.fixture
    def preferences(self):
        """Generation preferences"""
        return {
            "format": "chronological",
            "tone": "professional",
            "length": "two_pages"
        }
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_execution(self, resume_pipeline, complete_request, preferences):
        """Test complete pipeline execution with real data"""
        result = await resume_pipeline.execute(complete_request, preferences)
        
        assert isinstance(result, PipelineResult)
        assert result.resume_content is not None
        assert len(result.resume_content) > 0
        assert result.processing_time > 0
        assert len(result.stages_completed) == 5  # All 5 stages should complete
        assert result.quality_score >= 0
        assert result.quality_score <= 1
    
    @pytest.mark.asyncio
    async def test_pipeline_stages_integration(self, resume_pipeline, complete_request):
        """Test that all pipeline stages work together correctly"""
        result = await resume_pipeline.execute(complete_request)
        
        # Check that all stages completed
        expected_stages = [
            "skill_analysis",
            "job_alignment",
            "content_generation",
            "ats_optimization",
            "quality_validation"
        ]
        
        for stage in expected_stages:
            assert stage in result.stages_completed
        
        # Check metadata contains results from all stages
        metadata = result.metadata
        assert "skill_analysis" in metadata
        assert "job_alignment" in metadata
        assert "ats_optimization" in metadata
        assert "quality_validation" in metadata
    
    @pytest.mark.asyncio
    async def test_skill_analysis_integration(self, resume_pipeline, complete_request):
        """Test skill analysis stage integration"""
        result = await resume_pipeline.execute(complete_request)
        
        skill_analysis = result.metadata["skill_analysis"]
        
        assert "expanded_skills" in skill_analysis
        assert "skill_categories" in skill_analysis
        assert "proficiency_levels" in skill_analysis
        assert "recommended_additions" in skill_analysis
        
        # Should expand skills based on job requirements
        expanded_skills = skill_analysis["expanded_skills"]
        assert len(expanded_skills) > 0
        
        # Should categorize skills
        skill_categories = skill_analysis["skill_categories"]
        assert len(skill_categories) > 0
    
    @pytest.mark.asyncio
    async def test_job_alignment_integration(self, resume_pipeline, complete_request):
        """Test job alignment stage integration"""
        result = await resume_pipeline.execute(complete_request)
        
        job_alignment = result.metadata["job_alignment"]
        
        assert "alignment_score" in job_alignment
        assert "matched_requirements" in job_alignment
        assert "missing_requirements" in job_alignment
        assert "strength_areas" in job_alignment
        assert "improvement_areas" in job_alignment
        
        # Should calculate alignment score
        alignment_score = job_alignment["alignment_score"]
        assert 0 <= alignment_score <= 1
    
    @pytest.mark.asyncio
    async def test_content_generation_integration(self, resume_pipeline, complete_request):
        """Test content generation stage integration"""
        result = await resume_pipeline.execute(complete_request)
        
        content = result.resume_content
        
        # Should generate all required sections
        required_sections = ["summary", "experience", "education", "skills"]
        for section in required_sections:
            assert any(section.lower() in key.lower() for key in content.keys())
        
        # Each section should have content
        for section_data in content.values():
            assert "content" in section_data
            assert len(section_data["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_ats_optimization_integration(self, resume_pipeline, complete_request):
        """Test ATS optimization stage integration"""
        result = await resume_pipeline.execute(complete_request)
        
        ats_optimization = result.metadata["ats_optimization"]
        
        assert "ats_score" in ats_optimization
        assert "recommendations" in ats_optimization
        assert "keyword_density" in ats_optimization
        assert "compliance_score" in ats_optimization
        
        # Should calculate ATS score
        ats_score = ats_optimization["ats_score"]
        assert 0 <= ats_score <= 1
    
    @pytest.mark.asyncio
    async def test_quality_validation_integration(self, resume_pipeline, complete_request):
        """Test quality validation stage integration"""
        result = await resume_pipeline.execute(complete_request)
        
        quality_validation = result.metadata["quality_validation"]
        
        assert "overall_score" in quality_validation
        assert "word_count" in quality_validation
        assert "quality_issues" in quality_validation
        assert "validation_passed" in quality_validation
        
        # Should calculate quality score
        overall_score = quality_validation["overall_score"]
        assert 0 <= overall_score <= 1
    
    @pytest.mark.asyncio
    async def test_pipeline_with_minimal_data(self, resume_pipeline):
        """Test pipeline with minimal input data"""
        minimal_request = {
            "user_profile": {
                "name": "Test User",
                "experience": [],
                "education": [],
                "skills": []
            },
            "job_description": {
                "title": "Test Job",
                "requirements": [],
                "responsibilities": []
            }
        }
        
        result = await resume_pipeline.execute(minimal_request)
        
        # Should still generate basic structure
        assert isinstance(result, PipelineResult)
        assert result.resume_content is not None
        assert len(result.stages_completed) > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, resume_pipeline):
        """Test pipeline error handling with invalid data"""
        invalid_request = {
            "user_profile": None,  # Invalid profile
            "job_description": {}
        }
        
        result = await resume_pipeline.execute(invalid_request)
        
        # Should handle errors gracefully
        assert isinstance(result, PipelineResult)
        assert result.quality_score == 0.0
        assert "error" in result.metadata
    
    @pytest.mark.asyncio
    async def test_pipeline_performance(self, resume_pipeline, complete_request):
        """Test pipeline performance metrics"""
        import time
        
        start_time = time.time()
        result = await resume_pipeline.execute(complete_request)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert result.processing_time > 0
        assert result.processing_time < 30  # Should complete within 30 seconds
        
        # Processing time should be accurate
        actual_time = end_time - start_time
        assert abs(result.processing_time - actual_time) < 1.0  # Within 1 second tolerance
    
    @pytest.mark.asyncio
    async def test_pipeline_component_integration(self, resume_pipeline):
        """Test that pipeline components are properly integrated"""
        status = await resume_pipeline.get_pipeline_status()
        
        assert status["stages"] == resume_pipeline.pipeline_stages
        assert status["total_stages"] == 5
        
        # Check that all components are initialized
        components = status["components"]
        for component_name, status_value in components.items():
            assert status_value == "initialized"
    
    @pytest.mark.asyncio
    async def test_pipeline_with_preferences(self, resume_pipeline, complete_request):
        """Test pipeline with custom preferences"""
        custom_preferences = {
            "format": "functional",
            "tone": "casual",
            "length": "one_page"
        }
        
        result = await resume_pipeline.execute(complete_request, custom_preferences)
        
        assert isinstance(result, PipelineResult)
        assert result.resume_content is not None
        
        # Preferences should affect the output
        metadata = result.metadata
        assert "processing_time" in metadata
    
    @pytest.mark.asyncio
    async def test_pipeline_consistency(self, resume_pipeline, complete_request):
        """Test pipeline produces consistent results"""
        # Run pipeline twice with same input
        result1 = await resume_pipeline.execute(complete_request)
        result2 = await resume_pipeline.execute(complete_request)
        
        # Results should be consistent
        assert result1.quality_score == result2.quality_score
        assert len(result1.resume_content) == len(result2.resume_content)
        assert len(result1.stages_completed) == len(result2.stages_completed)

if __name__ == "__main__":
    pytest.main([__file__])

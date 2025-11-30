"""
Integration Tests for Resume Engine API Endpoints
LEVEL 5 - Integration tests for API endpoints
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from ...api.v1.endpoints.generate_resume import ResumeGenerationEndpoint
from ...api.v1.endpoints.validate_resume import ResumeValidationEndpoint
from ...api.v1.endpoints.healthcheck import HealthCheckEndpoint
from ...services.pipelines.resume_pipeline import ResumePipeline

class TestResumeAPIEndpointsIntegration:
    """Integration tests for resume API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing"""
        app = FastAPI()
        
        # Include routers from endpoints
        from ...api.v1.endpoints.generate_resume import router as generate_router
        from ...api.v1.endpoints.validate_resume import router as validate_router
        from ...api.v1.endpoints.healthcheck import router as health_router
        
        app.include_router(generate_router, prefix="/generate")
        app.include_router(validate_router, prefix="/validate")
        app.include_router(health_router, prefix="/health")
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_resume_request(self):
        """Sample resume generation request"""
        return {
            "user_profile": {
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
                "skills": ["Python", "JavaScript", "SQL", "AWS"]
            },
            "job_description": {
                "title": "Senior Software Engineer",
                "company": "Innovation Inc",
                "requirements": [
                    "5+ years of software development experience",
                    "Proficiency in Python and cloud technologies"
                ],
                "responsibilities": [
                    "Develop and maintain scalable software solutions"
                ]
            },
            "preferences": {
                "format": "chronological",
                "tone": "professional",
                "length": "one_page"
            }
        }
    
    @pytest.mark.asyncio
    async def test_generate_resume_endpoint_integration(self, client, sample_resume_request):
        """Test resume generation endpoint integration"""
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            # Mock pipeline response
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {"title": "Professional Summary", "content": ["Test summary"]},
                "experience": {"title": "Experience", "content": ["Test experience"]},
                "education": {"title": "Education", "content": ["Test education"]},
                "skills": {"title": "Skills", "content": ["Test skills"]}
            }
            mock_result.metadata = {"word_count": 150, "processing_time": 2.5}
            mock_result.processing_time = 2.5
            mock_result.quality_score = 0.85
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Test endpoint
            response = client.post("/generate", json=sample_resume_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "success" in data
            assert "resume_content" in data
            assert "metadata" in data
            assert "processing_time" in data
            
            # Verify pipeline was called with correct data
            mock_pipeline_instance.execute.assert_called_once()
            call_args = mock_pipeline_instance.execute.call_args[0][0]
            assert "user_profile" in call_args
            assert "job_description" in call_args
    
    @pytest.mark.asyncio
    async def test_validate_resume_endpoint_integration(self, client, sample_resume_request):
        """Test resume validation endpoint integration"""
        with patch('...services.utils.scoring.ResumeScorer') as mock_scorer:
            # Mock scorer response
            mock_scorer_instance = AsyncMock()
            mock_scorer.return_value = mock_scorer_instance
            
            mock_score_result = {
                "overall_score": 0.78,
                "grade": "B",
                "individual_scores": {
                    "ats_score": Mock(score=0.8),
                    "content_quality": Mock(score=0.75),
                    "job_alignment": Mock(score=0.8),
                    "readability": Mock(score=0.85),
                    "completeness": Mock(score=0.7)
                },
                "recommendations": ["Add more quantifiable achievements"],
                "strengths": ["Strong technical skills"],
                "improvement_areas": ["Content completeness"]
            }
            mock_scorer_instance.calculate_comprehensive_score.return_value = mock_score_result
            
            # Test endpoint
            response = client.post("/validate", json=sample_resume_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "success" in data
            assert "resume_content" in data
            assert "metadata" in data
            
            # Verify validation metadata
            metadata = data["metadata"]
            assert "ats_score" in metadata
            assert "validation_results" in metadata
            assert "recommendations" in metadata
    
    def test_healthcheck_endpoint_integration(self, client):
        """Test health check endpoint integration"""
        with patch('...api.v1.endpoints.healthcheck.HealthCheckEndpoint') as mock_health:
            # Mock health check response
            mock_health_instance = Mock()
            mock_health.return_value = mock_health_instance
            
            mock_status = {
                "status": "healthy",
                "uptime_seconds": 3600,
                "components": {
                    "section_generator": True,
                    "resume_pipeline": True,
                    "ats_optimizer": True
                },
                "version": "1.0.0",
                "timestamp": "2023-12-01T12:00:00Z"
            }
            mock_health_instance.get_system_status.return_value = mock_status
            
            # Test endpoint
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "status" in data
            assert "uptime_seconds" in data
            assert "components" in data
            assert "version" in data
            assert "timestamp" in data
    
    def test_healthcheck_ping_endpoint(self, client):
        """Test health check ping endpoint"""
        response = client.get("/health/ping")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "ok"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_generate_resume_error_handling(self, client):
        """Test generate resume endpoint error handling"""
        # Test with missing required fields
        invalid_request = {
            "user_profile": {
                "name": "John Doe"
                # Missing required fields
            },
            "job_description": {}
        }
        
        response = client.post("/generate", json=invalid_request)
        
        # Should return error for missing required data
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_validate_resume_error_handling(self, client):
        """Test validate resume endpoint error handling"""
        with patch('...services.utils.scoring.ResumeScorer') as mock_scorer:
            # Mock scorer to raise exception
            mock_scorer_instance = AsyncMock()
            mock_scorer.return_value = mock_scorer_instance
            mock_scorer_instance.calculate_comprehensive_score.side_effect = Exception("Scoring failed")
            
            # Test endpoint
            response = client.post("/validate", json={
                "user_profile": {"name": "Test"},
                "job_description": {}
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "failed" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_resume_with_preferences(self, client, sample_resume_request):
        """Test generate resume endpoint with custom preferences"""
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {"summary": {"content": ["Test"]}}
            mock_result.metadata = {"word_count": 150}
            mock_result.processing_time = 2.0
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Add custom preferences
            sample_resume_request["preferences"] = {
                "format": "functional",
                "tone": "casual",
                "length": "two_pages"
            }
            
            response = client.post("/generate", json=sample_resume_request)
            
            assert response.status_code == 200
            
            # Verify preferences were passed to pipeline
            call_args = mock_pipeline_instance.execute.call_args
            assert len(call_args[0]) == 2  # request and preferences
            preferences = call_args[0][1]
            assert preferences["format"] == "functional"
            assert preferences["tone"] == "casual"
    
    @pytest.mark.asyncio
    async def test_api_response_format_consistency(self, client, sample_resume_request):
        """Test that API responses have consistent format"""
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {"title": "Summary", "content": ["Test"]},
                "experience": {"title": "Experience", "content": ["Test"]},
                "education": {"title": "Education", "content": ["Test"]},
                "skills": {"title": "Skills", "content": ["Test"]}
            }
            mock_result.metadata = {"word_count": 150}
            mock_result.processing_time = 2.0
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            response = client.post("/generate", json=sample_resume_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "success" in data
            assert "resume_content" in data
            assert "metadata" in data
            assert "processing_time" in data
            
            # Check resume content structure
            resume_content = data["resume_content"]
            for section_name, section_data in resume_content.items():
                assert "title" in section_data
                assert "content" in section_data
                assert isinstance(section_data["content"], list)
    
    @pytest.mark.asyncio
    async def test_api_performance_metrics(self, client, sample_resume_request):
        """Test API performance metrics collection"""
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {"summary": {"content": ["Test"]}}
            mock_result.metadata = {
                "word_count": 150,
                "processing_time": 2.5,
                "ats_score": 0.85,
                "validation_results": {"grammar_score": 0.9}
            }
            mock_result.processing_time = 2.5
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            response = client.post("/generate", json=sample_resume_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that performance metrics are included
            metadata = data["metadata"]
            assert "processing_time" in metadata
            assert "word_count" in metadata
            assert "ats_score" in metadata
            assert "validation_results" in metadata
    
    def test_api_cors_headers(self, client):
        """Test that API includes appropriate CORS headers"""
        response = client.options("/generate")
        
        # Should include CORS headers for cross-origin requests
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

if __name__ == "__main__":
    pytest.main([__file__])

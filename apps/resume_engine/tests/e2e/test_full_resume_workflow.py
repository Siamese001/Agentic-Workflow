"""
End-to-End Tests for Resume Engine Full Workflow
LEVEL 5 - E2E tests for complete resume generation workflow
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from ...cli.run_resume_engine import ResumeEngineCLI
from ...workers.resume_generate_worker import ResumeGenerateWorker, ResumeGenerateTask
from ...workers.enrichment_worker import EnrichmentWorker, EnrichmentTask
from ...services.pipelines.resume_pipeline import ResumePipeline

class TestResumeEngineE2E:
    """End-to-end tests for complete resume engine workflow"""
    
    @pytest.fixture
    def cli(self):
        """Create CLI instance for testing"""
        return ResumeEngineCLI()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_profile_file(self, temp_dir):
        """Create sample user profile file"""
        profile_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "phone": "555-0123",
            "experience": [
                {
                    "company": "DataTech Solutions",
                    "position": "Senior Data Engineer",
                    "start_date": "2019-06",
                    "end_date": "2023-11",
                    "description": "Led data pipeline development, improved processing efficiency by 45%, and mentored team of 4 engineers."
                },
                {
                    "company": "Analytics Corp",
                    "position": "Data Engineer",
                    "start_date": "2017-03",
                    "end_date": "2019-05",
                    "description": "Built ETL pipelines, implemented data quality checks, and collaborated with data science team."
                }
            ],
            "education": [
                {
                    "institution": "Tech University",
                    "degree": "Master of Science in Data Science",
                    "graduation_year": 2017
                },
                {
                    "institution": "State College",
                    "degree": "Bachelor of Science in Computer Science",
                    "graduation_year": 2015
                }
            ],
            "skills": [
                "Python", "SQL", "Apache Spark", "AWS", "Docker", "Kubernetes",
                "Data Warehousing", "ETL", "Machine Learning", "Statistics",
                "Team Leadership", "Project Management", "Communication"
            ]
        }
        
        profile_file = Path(temp_dir) / "profile.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        return str(profile_file)
    
    @pytest.fixture
    def sample_job_file(self, temp_dir):
        """Create sample job description file"""
        job_data = {
            "title": "Principal Data Engineer",
            "company": "CloudScale Analytics",
            "requirements": [
                "8+ years of data engineering experience",
                "Expertise in Python and SQL",
                "Strong background in cloud platforms (AWS preferred)",
                "Experience with big data technologies (Spark, Hadoop)",
                "Leadership experience and team mentoring",
                "Knowledge of machine learning pipelines",
                "Excellent communication and collaboration skills"
            ],
            "responsibilities": [
                "Lead design and implementation of scalable data pipelines",
                "Mentor and develop senior data engineering team",
                "Drive data architecture decisions and best practices",
                "Collaborate with data science and analytics teams",
                "Ensure data quality and governance standards"
            ]
        }
        
        job_file = Path(temp_dir) / "job.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return str(job_file)
    
    @pytest.mark.asyncio
    async def test_complete_cli_workflow(self, cli, sample_profile_file, sample_job_file, temp_dir):
        """Test complete CLI workflow from file input to resume output"""
        output_file = Path(temp_dir) / "generated_resume.json"
        
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            # Mock pipeline response
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {
                    "title": "Professional Summary",
                    "content": ["Results-oriented data engineer with 6+ years of experience building scalable data solutions and leading technical teams."]
                },
                "experience": {
                    "title": "Professional Experience",
                    "content": [
                        "Senior Data Engineer - DataTech Solutions (2019-2023)",
                        "• Led data pipeline development improving efficiency by 45%",
                        "• Mentored team of 4 engineers and implemented best practices",
                        "• Designed and implemented cloud-native data architecture",
                        "Data Engineer - Analytics Corp (2017-2019)",
                        "• Built ETL pipelines processing 10TB+ data daily",
                        "• Implemented data quality checks reducing errors by 30%",
                        "• Collaborated with data science team on ML model deployment"
                    ]
                },
                "education": {
                    "title": "Education",
                    "content": [
                        "Master of Science in Data Science - Tech University (2017)",
                        "Bachelor of Science in Computer Science - State College (2015)"
                    ]
                },
                "skills": {
                    "title": "Skills & Expertise",
                    "content": [
                        "Technical Skills:",
                        "• Python, SQL, Apache Spark, AWS, Docker, Kubernetes",
                        "• Data Warehousing, ETL, Machine Learning, Statistics",
                        "Soft Skills:",
                        "• Team Leadership, Project Management, Communication"
                    ]
                }
            }
            mock_result.metadata = {
                "word_count": 280,
                "processing_time": 3.2,
                "ats_score": 0.88,
                "validation_results": {"grammar_score": 0.95}
            }
            mock_result.processing_time = 3.2
            mock_result.quality_score = 0.87
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Execute CLI workflow
            result = await cli.generate_resume(
                sample_profile_file, 
                sample_job_file, 
                str(output_file)
            )
            
            # Verify result
            assert result is not None
            assert result.resume_content is not None
            assert result.quality_score == 0.87
            assert result.processing_time == 3.2
            
            # Verify output file was created
            assert output_file.exists()
            
            # Verify output file content
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
            
            assert "content" in saved_data
            assert "metadata" in saved_data
            assert len(saved_data["content"]) > 0
            
            # Verify pipeline was called correctly
            mock_pipeline_instance.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_resume_analysis_workflow(self, cli, sample_profile_file, sample_job_file, temp_dir):
        """Test resume analysis workflow"""
        # First generate a resume
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {"content": ["Test summary"]},
                "experience": {"content": ["Test experience"]},
                "education": {"content": ["Test education"]},
                "skills": {"content": ["Test skills"]}
            }
            mock_result.metadata = {"word_count": 200}
            mock_result.processing_time = 2.0
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Generate resume
            resume_file = Path(temp_dir) / "resume.json"
            await cli.generate_resume(sample_profile_file, sample_job_file, str(resume_file))
        
        # Then analyze the resume
        with patch('...services.utils.scoring.ResumeScorer') as mock_scorer:
            mock_scorer_instance = AsyncMock()
            mock_scorer.return_value = mock_scorer_instance
            
            mock_score_result = {
                "overall_score": 0.82,
                "grade": "B",
                "individual_scores": {
                    "ats_score": Mock(score=0.85),
                    "content_quality": Mock(score=0.80),
                    "job_alignment": Mock(score=0.82),
                    "readability": Mock(score=0.88),
                    "completeness": Mock(score=0.75)
                },
                "recommendations": [
                    "Add more quantifiable achievements",
                    "Include specific technical metrics",
                    "Expand leadership experience details"
                ],
                "strengths": ["Strong technical skills", "Good experience progression"],
                "improvement_areas": ["Content completeness", "Quantification"]
            }
            mock_scorer_instance.calculate_comprehensive_score.return_value = mock_score_result
            
            # Analyze resume
            analysis_result = await cli.analyze_resume(str(resume_file), sample_job_file)
            
            # Verify analysis results
            assert analysis_result["overall_score"] == 0.82
            assert analysis_result["grade"] == "B"
            assert len(analysis_result["recommendations"]) > 0
            assert len(analysis_result["strengths"]) > 0
            assert len(analysis_result["improvement_areas"]) > 0
    
    @pytest.mark.asyncio
    async def test_resume_enrichment_workflow(self, cli, sample_profile_file, sample_job_file, temp_dir):
        """Test resume enrichment workflow"""
        # First generate a basic resume
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {"content": ["Basic summary"]},
                "experience": {"content": ["Basic experience"]},
                "education": {"content": ["Basic education"]},
                "skills": {"content": ["Basic skills"]}
            }
            mock_result.metadata = {"word_count": 150}
            mock_result.processing_time = 1.5
            mock_result.quality_score = 0.7
            mock_pipeline_instance.execute.return_value = mock_result
            
            resume_file = Path(temp_dir) / "basic_resume.json"
            await cli.generate_resume(sample_profile_file, sample_job_file, str(resume_file))
        
        # Load the generated resume for enrichment
        with open(resume_file, 'r') as f:
            resume_content = json.load(f)["content"]
        
        # Test comprehensive enrichment
        with patch('...workers.enrichment_worker.EnrichmentWorker') as mock_enrichment_worker:
            mock_worker_instance = AsyncMock()
            mock_enrichment_worker.return_value = mock_worker_instance
            
            mock_enrichment_result = {
                "enrichment_type": "comprehensive",
                "comprehensive_score": 0.89,
                "individual_results": {
                    "skills": {
                        "expanded_skills": ["Python", "SQL", "Apache Spark", "AWS", "Docker", "Kubernetes"],
                        "skill_categories": {"programming_languages": ["Python", "SQL"], "cloud_platforms": ["AWS"]}
                    },
                    "ats": {
                        "ats_score": 0.92,
                        "recommendations": ["Add more keywords from job description"]
                    },
                    "alignment": {
                        "alignment_score": 0.85,
                        "matched_requirements": ["Python", "AWS", "Leadership"]
                    }
                },
                "enriched_resume": {
                    "summary": {"content": ["Enhanced summary with more details"]},
                    "experience": {"content": ["Enhanced experience with quantified achievements"]},
                    "education": {"content": ["Enhanced education"]},
                    "skills": {"content": ["Enhanced skills with expanded list"]}
                },
                "total_recommendations": [
                    "Add more quantifiable achievements",
                    "Include specific technical metrics",
                    "Expand cloud platform experience"
                ]
            }
            
            mock_worker_instance._perform_enrichment.return_value = mock_enrichment_result
            
            # Create enrichment worker instance
            enrichment_worker = EnrichmentWorker()
            
            # Create enrichment task
            task = EnrichmentTask(
                task_id="e2e_test_enrichment",
                resume_id="test_resume",
                resume_content=resume_content,
                enrichment_type="comprehensive",
                job_description=json.load(open(sample_job_file))
            )
            
            # Execute enrichment
            enrichment_result = await enrichment_worker._perform_enrichment(task)
            
            # Verify enrichment results
            assert enrichment_result["enrichment_type"] == "comprehensive"
            assert enrichment_result["comprehensive_score"] == 0.89
            assert "individual_results" in enrichment_result
            assert "enriched_resume" in enrichment_result
            assert len(enrichment_result["total_recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_worker_system_integration(self, temp_dir):
        """Test worker system integration with task processing"""
        # Test resume generation worker
        resume_worker = ResumeGenerateWorker()
        
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            mock_result = Mock()
            mock_result.resume_content = {"summary": {"content": ["Worker test"]}}
            mock_result.metadata = {"word_count": 100}
            mock_result.processing_time = 1.0
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Create test task
            task = ResumeGenerateTask(
                task_id="worker_test_001",
                user_id="test_user",
                user_profile={"name": "Test User", "skills": ["Python"]},
                job_description={"title": "Test Job"},
                preferences={}
            )
            
            # Process task
            result = await resume_worker._generate_resume(task)
            
            # Verify result
            assert result["success"] is True
            assert "resume_id" in result
            assert result["quality_score"] == 0.8
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, cli, temp_dir):
        """Test error handling throughout the workflow"""
        # Test with invalid profile file
        invalid_profile_file = Path(temp_dir) / "invalid.json"
        with open(invalid_profile_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle file loading error gracefully
        with pytest.raises(Exception):
            await cli.generate_resume(str(invalid_profile_file), sample_job_file)
        
        # Test with missing job file
        missing_job_file = Path(temp_dir) / "missing.json"
        
        # Should handle missing file error gracefully
        with pytest.raises(Exception):
            await cli.generate_resume(sample_profile_file, str(missing_job_file))
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, cli, sample_profile_file, sample_job_file, temp_dir):
        """Test performance benchmarks for the complete workflow"""
        import time
        
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            # Simulate realistic processing time
            async def realistic_execute(*args, **kwargs):
                await asyncio.sleep(0.5)  # Simulate processing delay
                mock_result = Mock()
                mock_result.resume_content = {"summary": {"content": ["Performance test"]}}
                mock_result.metadata = {"word_count": 200}
                mock_result.processing_time = 0.5
                mock_result.quality_score = 0.85
                return mock_result
            
            mock_pipeline_instance.execute.side_effect = realistic_execute
            
            # Measure performance
            start_time = time.time()
            result = await cli.generate_resume(sample_profile_file, sample_job_file)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Performance assertions
            assert total_time < 5.0  # Should complete within 5 seconds
            assert result.processing_time > 0
            assert result.quality_score >= 0
    
    @pytest.mark.asyncio
    async def test_data_consistency_workflow(self, cli, sample_profile_file, sample_job_file, temp_dir):
        """Test data consistency throughout the workflow"""
        # Generate resume multiple times with same input
        results = []
        
        with patch('...services.pipelines.resume_pipeline.ResumePipeline') as mock_pipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline.return_value = mock_pipeline_instance
            
            # Create consistent mock response
            mock_result = Mock()
            mock_result.resume_content = {
                "summary": {"content": ["Consistent summary"]},
                "experience": {"content": ["Consistent experience"]},
                "education": {"content": ["Consistent education"]},
                "skills": {"content": ["Consistent skills"]}
            }
            mock_result.metadata = {"word_count": 200}
            mock_result.processing_time = 2.0
            mock_result.quality_score = 0.8
            mock_pipeline_instance.execute.return_value = mock_result
            
            # Generate resume 3 times
            for i in range(3):
                output_file = Path(temp_dir) / f"resume_{i}.json"
                result = await cli.generate_resume(sample_profile_file, sample_job_file, str(output_file))
                results.append(result)
            
            # Verify consistency
            for result in results:
                assert result.quality_score == 0.8
                assert result.processing_time == 2.0
                assert len(result.resume_content) == 4

if __name__ == "__main__":
    pytest.main([__file__])

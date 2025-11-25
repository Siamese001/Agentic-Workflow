"""
Shared Test Data Fixtures

Provides common test data, mock objects, and fixtures used across all test layers.
Ensures consistency and reduces duplication in test implementations.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid

# Mark all tests in this module as shared fixtures
pytestmark = [pytest.mark.shared, pytest.mark.fixture]


@dataclass(frozen=True)
class ResumeTestData:
    """Standard resume test data fixture."""
    candidate_name: str
    contact_info: Dict[str, str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[str]
    projects: List[Dict[str, Any]]


@dataclass(frozen=True)
class JobDescriptionTestData:
    """Standard job description test data fixture."""
    job_id: str
    title: str
    company: str
    location: str
    requirements: List[str]
    responsibilities: List[str]
    qualifications: Dict[str, Any]
    description: str


@dataclass(frozen=True)
class WorkflowTestData:
    """Standard workflow test data fixture."""
    workflow_id: str
    mission: str
    input_data: Dict[str, Any]
    expected_steps: List[str]
    configuration: Dict[str, Any]


class TestResumeFixtures:
    """Test resume data fixtures."""
    
    @pytest.fixture
    def sample_resume_software_engineer(self):
        """Sample software engineer resume for testing."""
        return ResumeTestData(
            candidate_name="John Doe",
            contact_info={
                "email": "john.doe@email.com",
                "phone": "+1-555-1234",
                "linkedin": "https://linkedin.com/in/johndoe"
            },
            experience=[
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "location": "San Francisco, CA",
                    "dates": {"start": "2020-01", "end": "2024-12"},
                    "bullet_points": [
                        "Developed scalable microservices using Python and AWS",
                        "Led team of 5 engineers on major product launch",
                        "Improved system performance by 40%"
                    ]
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "location": "Austin, TX",
                    "dates": {"start": "2018-06", "end": "2019-12"},
                    "bullet_points": [
                        "Built REST APIs using Django and PostgreSQL",
                        "Implemented CI/CD pipelines",
                        "Collaborated with cross-functional teams"
                    ]
                }
            ],
            education=[
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "university": "State University",
                    "location": "Boston, MA",
                    "graduation": "2018-05"
                }
            ],
            skills=["Python", "Django", "AWS", "PostgreSQL", "Docker", "Kubernetes", "JavaScript", "React"],
            certifications=["AWS Certified Solutions Architect", "Docker Certified Associate"],
            projects=[
                {
                    "name": "E-commerce Platform",
                    "description": "Built full-stack e-commerce platform",
                    "technologies": ["Python", "Django", "React", "PostgreSQL"],
                    "highlights": ["Handled 10k+ concurrent users", "95% uptime"]
                }
            ]
        )
    
    @pytest.fixture
    def sample_resume_data_scientist(self):
        """Sample data scientist resume for testing."""
        return ResumeTestData(
            candidate_name="Jane Smith",
            contact_info={
                "email": "jane.smith@email.com",
                "phone": "+1-555-5678",
                "linkedin": "https://linkedin.com/in/janesmith"
            },
            experience=[
                {
                    "title": "Senior Data Scientist",
                    "company": "DataCorp",
                    "location": "New York, NY",
                    "dates": {"start": "2019-03", "end": "2024-12"},
                    "bullet_points": [
                        "Developed machine learning models for fraud detection",
                        "Analyzed large datasets using Python and R",
                        "Improved prediction accuracy by 25%"
                    ]
                }
            ],
            education=[
                {
                    "degree": "Master of Science",
                    "field": "Data Science",
                    "university": "Tech Institute",
                    "location": "Stanford, CA",
                    "graduation": "2019-02"
                }
            ],
            skills=["Python", "R", "TensorFlow", "PyTorch", "SQL", "Machine Learning", "Statistics"],
            certifications=["Google Cloud ML Engineer", "TensorFlow Developer Certificate"],
            projects=[
                {
                    "name": "Customer Churn Prediction",
                    "description": "ML model to predict customer churn",
                    "technologies": ["Python", "TensorFlow", "Pandas"],
                    "highlights": ["Reduced churn by 15%", "Deployed to production"]
                }
            ]
        )
    
    @pytest.fixture
    def sample_resume_career_changer(self):
        """Sample career changer resume for testing."""
        return ResumeTestData(
            candidate_name="Michael Chen",
            contact_info={
                "email": "michael.chen@email.com",
                "phone": "+1-555-9012",
                "linkedin": "https://linkedin.com/in/michaelchen"
            },
            experience=[
                {
                    "title": "Senior Software Engineer",
                    "company": "SoftwareInc",
                    "location": "Seattle, WA",
                    "dates": {"start": "2016-08", "end": "2024-12"},
                    "bullet_points": [
                        "Led development of enterprise software solutions",
                        "Managed technical team of 8 engineers",
                        "Coordinated with product management on roadmap planning"
                    ]
                }
            ],
            education=[
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Engineering",
                    "university": "Engineering University",
                    "location": "Los Angeles, CA",
                    "graduation": "2016-05"
                },
                {
                    "degree": "MBA (In Progress)",
                    "field": "Business Administration",
                    "university": "Business School",
                    "location": "Online",
                    "graduation": "2025-12"
                }
            ],
            skills=["Java", "Spring Boot", "Python", "Leadership", "Product Strategy", "Agile", "Stakeholder Management"],
            certifications=["PMP Certification", "Scrum Master"],
            projects=[
                {
                    "name": "Product Launch Coordination",
                    "description": "Led cross-functional team for product launch",
                    "technologies": ["Project Management", "Stakeholder Communication"],
                    "highlights": ["Launched on time", "20% user adoption increase"]
                }
            ]
        )


class TestJobDescriptionFixtures:
    """Test job description data fixtures."""
    
    @pytest.fixture
    def sample_job_software_engineer(self):
        """Sample software engineer job description for testing."""
        return JobDescriptionTestData(
            job_id="job_001",
            title="Senior Software Engineer",
            company="TechCorp",
            location="San Francisco, CA",
            requirements=[
                "5+ years of software development experience",
                "Proficiency in Python and JavaScript",
                "Experience with cloud platforms (AWS preferred)",
                "Strong problem-solving skills",
                "Bachelor's degree in Computer Science or related field"
            ],
            responsibilities=[
                "Design and develop scalable software solutions",
                "Collaborate with cross-functional teams",
                "Participate in code reviews and mentorship",
                "Troubleshoot and optimize application performance"
            ],
            qualifications={
                "min_experience_years": 5,
                "required_skills": ["Python", "JavaScript", "AWS"],
                "preferred_skills": ["Docker", "Kubernetes", "React"],
                "education_level": "Bachelor's",
                "remote_work": True
            },
            description="""We are looking for a Senior Software Engineer to join our growing team. 
            You will be responsible for developing high-quality software solutions, 
            working with modern technologies, and contributing to our product roadmap."""
        )
    
    @pytest.fixture
    def sample_job_data_scientist(self):
        """Sample data scientist job description for testing."""
        return JobDescriptionTestData(
            job_id="job_002",
            title="Senior Data Scientist",
            company="DataCorp",
            location="New York, NY",
            requirements=[
                "4+ years of data science experience",
                "Strong programming skills in Python and R",
                "Experience with machine learning frameworks",
                "Advanced degree in quantitative field preferred",
                "Excellent communication skills"
            ],
            responsibilities=[
                "Develop and deploy machine learning models",
                "Analyze complex datasets to derive insights",
                "Collaborate with business stakeholders",
                "Present findings to executive leadership"
            ],
            qualifications={
                "min_experience_years": 4,
                "required_skills": ["Python", "R", "Machine Learning"],
                "preferred_skills": ["TensorFlow", "PyTorch", "SQL"],
                "education_level": "Master's",
                "remote_work": False
            },
            description="""Join our data science team to work on challenging problems 
            in fraud detection and customer analytics. You'll have the opportunity 
            to work with cutting-edge ML technologies and large-scale datasets."""
        )
    
    @pytest.fixture
    def sample_job_product_manager(self):
        """Sample product manager job description for testing."""
        return JobDescriptionTestData(
            job_id="job_003",
            title="Product Manager",
            company="ProductInc",
            location="Remote",
            requirements=[
                "3+ years of product management experience",
                "Technical background or experience",
                "Strong analytical and communication skills",
                "Experience with agile development methodologies",
                "MBA or equivalent experience preferred"
            ],
            responsibilities=[
                "Define product roadmap and strategy",
                "Work with engineering teams on product development",
                "Gather and analyze customer feedback",
                "Present product vision to stakeholders"
            ],
            qualifications={
                "min_experience_years": 3,
                "required_skills": ["Product Strategy", "Stakeholder Management", "Agile"],
                "preferred_skills": ["Technical Background", "Data Analysis", "Leadership"],
                "education_level": "MBA",
                "remote_work": True
            },
            description="""We're seeking a Product Manager to drive our product strategy 
            and work closely with engineering and design teams. Ideal candidate has 
            technical background and strong business acumen."""
        )


class TestWorkflowFixtures:
    """Test workflow data fixtures."""
    
    @pytest.fixture
    def sample_workflow_resume_analysis(self):
        """Sample resume analysis workflow for testing."""
        return WorkflowTestData(
            workflow_id="workflow_001",
            mission="Analyze resume against job requirements and provide improvement suggestions",
            input_data={
                "resume_content": "Sample resume content...",
                "job_description": "Sample job description...",
                "analysis_type": "comprehensive"
            },
            expected_steps=[
                "extract_job_requirements",
                "parse_resume_content", 
                "analyze_skill_match",
                "identify_gaps",
                "generate_improvements"
            ],
            configuration={
                "analysis_depth": "detailed",
                "include_suggestions": True,
                "safety_checks": True,
                "telemetry_enabled": True
            }
        )
    
    @pytest.fixture
    def sample_workflow_batch_processing(self):
        """Sample batch processing workflow for testing."""
        return WorkflowTestData(
            workflow_id="workflow_batch_001",
            mission="Process multiple job applications in batch",
            input_data={
                "jobs": [
                    {"job_id": "job_1", "description": "Job 1 description"},
                    {"job_id": "job_2", "description": "Job 2 description"},
                    {"job_id": "job_3", "description": "Job 3 description"}
                ],
                "resume_content": "Sample resume content...",
                "batch_config": {"parallel_processing": True, "max_workers": 3}
            },
            expected_steps=[
                "validate_batch_input",
                "process_jobs_parallel",
                "aggregate_results",
                "generate_batch_report"
            ],
            configuration={
                "parallel_execution": True,
                "max_concurrent_jobs": 3,
                "error_handling": "continue_on_error",
                "timeout_per_job": 300
            }
        )


class TestMockResponseFixtures:
    """Test mock response fixtures for external services."""
    
    @pytest.fixture
    def mock_llm_responses(self):
        """Mock LLM responses for testing."""
        return {
            "analysis_response": {
                "requirements": ["Python", "AWS", "5+ years experience"],
                "skills_matched": ["Python", "AWS"],
                "skills_missing": ["Experience duration"],
                "match_score": 0.75,
                "confidence": 0.85
            },
            "improvement_response": {
                "suggested_additions": [
                    "Add specific project metrics",
                    "Highlight leadership experience",
                    "Include cloud deployment examples"
                ],
                "recommended_skills": ["Kubernetes", "DevOps practices"],
                "priority_areas": ["Experience quantification", "Technical depth"]
            },
            "safety_check_response": {
                "is_safe": True,
                "risk_level": "low",
                "concerns": [],
                "recommendations": ["Standard review sufficient"]
            }
        }
    
    @pytest.fixture
    def mock_api_responses(self):
        """Mock API responses for external services."""
        return {
            "job_parsing_api": {
                "status": "success",
                "parsed_requirements": {
                    "skills": ["Python", "AWS", "SQL"],
                    "experience": "5+ years",
                    "education": "Bachelor's degree"
                },
                "confidence": 0.92
            },
            "resume_parsing_api": {
                "status": "success", 
                "parsed_resume": {
                    "personal_info": {"name": "John Doe", "contact": "john@email.com"},
                    "experience": [{"title": "Software Engineer", "years": 6}],
                    "skills": ["Python", "Django", "AWS", "SQL"],
                    "education": [{"degree": "BS Computer Science"}]
                },
                "confidence": 0.88
            },
            "similarity_api": {
                "status": "success",
                "similarity_score": 0.78,
                "skill_match_score": 0.85,
                "experience_match_score": 0.70,
                "detailed_analysis": {
                    "matching_skills": ["Python", "AWS", "SQL"],
                    "missing_skills": ["Docker", "Kubernetes"],
                    "experience_gap": "1 year short of requirement"
                }
            }
        }


class TestConfigurationFixtures:
    """Test configuration fixtures."""
    
    @pytest.fixture
    def test_configurations(self):
        """Standard test configurations."""
        return {
            "execution_config": {
                "timeout_seconds": 300,
                "max_retries": 3,
                "retry_delay": 1.0,
                "circuit_breaker_threshold": 5
            },
            "safety_config": {
                "enable_content_filtering": True,
                "enable_injection_detection": True,
                "max_risk_level": "medium",
                "strict_mode": False
            },
            "memory_config": {
                "enable_temporal_kg": True,
                "cache_ttl_seconds": 3600,
                "max_triplets_per_query": 100,
                "enable_deduplication": True
            },
            "telemetry_config": {
                "enable_tracing": True,
                "log_level": "INFO",
                "metrics_collection": True,
                "cost_tracking": True
            }
        }
    
    @pytest.fixture
    def edge_case_configurations(self):
        """Edge case test configurations."""
        return {
            "minimal_config": {
                "timeout_seconds": 30,
                "max_retries": 1,
                "safety_checks": "basic_only"
            },
            "maximal_config": {
                "timeout_seconds": 1800,
                "max_retries": 10,
                "safety_checks": "comprehensive",
                "enable_all_features": True
            },
            "stress_test_config": {
                "timeout_seconds": 60,
                "max_retries": 0,
                "high_concurrency": True,
                "resource_limits": "strict"
            }
        }


class TestErrorScenarioFixtures:
    """Test error scenario fixtures."""
    
    @pytest.fixture
    def error_scenarios(self):
        """Common error scenarios for testing."""
        return {
            "network_timeout": {
                "error_type": "timeout",
                "message": "Request timed out after 30 seconds",
                "retryable": True,
                "expected_recovery": "retry_with_backoff"
            },
            "api_rate_limit": {
                "error_type": "rate_limit",
                "message": "API rate limit exceeded",
                "retryable": True,
                "expected_recovery": "exponential_backoff"
            },
            "invalid_input": {
                "error_type": "validation",
                "message": "Input validation failed: missing required field",
                "retryable": False,
                "expected_recovery": "request_user_correction"
            },
            "service_unavailable": {
                "error_type": "service_down",
                "message": "External service temporarily unavailable",
                "retryable": True,
                "expected_recovery": "use_fallback_service"
            },
            "safety_violation": {
                "error_type": "safety_policy",
                "message": "Content blocked by safety policy",
                "retryable": False,
                "expected_recovery": "block_execution"
            }
        }


# Utility functions for test data generation
def generate_test_resume(customizations: Optional[Dict[str, Any]] = None) -> ResumeTestData:
    """Generate a test resume with optional customizations."""
    base_resume = ResumeTestData(
        candidate_name="Test Candidate",
        contact_info={"email": "test@example.com", "phone": "+1-555-0000"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        projects=[]
    )
    
    if customizations:
        # Apply customizations (simplified for example)
        if "skills" in customizations:
            base_resume = base_resume._replace(skills=customizations["skills"])
        if "experience_years" in customizations:
            base_resume = base_resume._replace(
                experience=[{
                    "title": "Software Engineer",
                    "company": "Test Company",
                    "dates": {"start": f"{2024 - customizations['experience_years']}-01", "end": "2024-12"},
                    "bullet_points": ["Test experience"]
                }]
            )
    
    return base_resume


def generate_test_job(difficulty: str = "medium") -> JobDescriptionTestData:
    """Generate a test job description with specified difficulty."""
    if difficulty == "easy":
        requirements = ["Basic programming skills"]
        qualifications = {"min_experience_years": 0, "required_skills": ["Python"]}
    elif difficulty == "hard":
        requirements = ["10+ years experience", "PhD preferred", "Multiple certifications"]
        qualifications = {"min_experience_years": 10, "required_skills": ["Python", "AWS", "ML", "Leadership"]}
    else:  # medium
        requirements = ["3-5 years experience", "Bachelor's degree"]
        qualifications = {"min_experience_years": 3, "required_skills": ["Python", "SQL"]}
    
    return JobDescriptionTestData(
        job_id=f"test_job_{difficulty}",
        title=f"Test Position ({difficulty})",
        company="Test Company",
        location="Remote",
        requirements=requirements,
        responsibilities=["Test responsibilities"],
        qualifications=qualifications,
        description="Test job description"
    )

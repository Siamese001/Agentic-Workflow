"""L1 Planning Fixtures."""
import pytest

@pytest.fixture
def mock_workflow_config():
    """Fixture providing mock workflow configuration."""
    return {
        "profile_id": "test_profile",
        "enable_rag": True,
        "enable_qa": True,
        "safety_tier": "standard",
    }

@pytest.fixture
def mock_job_resume_pair():
    """Fixture providing mock job and resume pair."""
    return {
        "job": {
            "title": "Software Engineer",
            "requirements": ["Python", "AWS", "Docker"],
        },
        "resume": {
            "summary": "Experienced developer",
            "skills": ["Python", "JavaScript"],
        },
    }

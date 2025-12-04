"""L1 Planning Layer Fixtures."""
import pytest

@pytest.fixture
def mock_workflow_config():
    """Fixture providing mock workflow configuration."""
    return {
        "profile_id": "test_profile",
        "enable_rag": True,
        "enable_qa": True,
    }

@pytest.fixture
def mock_job_input():
    """Fixture providing mock job input."""
    return {
        "title": "Software Engineer",
        "requirements": ["Python", "AWS"],
    }

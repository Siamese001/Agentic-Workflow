"""Shared Test Fixtures."""
import pytest

@pytest.fixture
def mock_execution_context():
    """Shared fixture for mock execution context."""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "profile_name": "default",
    }

@pytest.fixture
def mock_config():
    """Shared fixture for mock configuration."""
    return {
        "profile_id": "test_profile",
        "enable_rag": True,
        "enable_qa": True,
    }

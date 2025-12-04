"""Common Shared Fixtures."""
import pytest

@pytest.fixture
def mock_workflow_context():
    """Fixture providing mock workflow context."""
    return {
        "workflow_id": "wf_001",
        "user_id": "user_001",
        "session_id": "session_001",
        "profile_name": "default",
    }

@pytest.fixture
def mock_agent_config():
    """Fixture providing mock agent configuration."""
    return {
        "agent_id": "agent_001",
        "type": "planner",
        "model_tier": "balanced",
        "max_tokens": 4096,
    }

"""Common test utilities and fixtures."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock


class TestHelper:
    """Helper class for common test operations."""

    @staticmethod
    def create_temp_dir():
        """Create temporary directory for tests."""
        return tempfile.mkdtemp()

    @staticmethod
    def cleanup_temp_dir(path):
        """Clean up temporary directory."""
        shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def mock_function_call(func_name, return_value=None):
        """Create a mock function call."""
        mock = Mock()
        mock.__name__ = func_name
        mock.return_value = return_value
        return mock

    @staticmethod
    def create_mock_agent(agent_id="test-agent", state="idle"):
        """Create a mock agent with default values."""
        agent = Mock()
        agent.id = agent_id
        agent.state = state
        agent.config = {}
        return agent

    @staticmethod
    def create_mock_config(config_dict=None):
        """Create a mock configuration."""
        config = Mock()
        if config_dict:
            for key, value in config_dict.items():
                setattr(config, key, value)
        return config


# Test templates for common patterns
class BasicTestTemplate:
    """Template for basic unit tests."""

    def __init__(self, module_name):
        self.module_name = module_name
        self.mocks = {}

    def setup_mocks(self, mock_names):
        """Set up multiple mocks."""
        for name in mock_names:
            self.mocks[name] = Mock()

    def get_mock(self, name):
        """Get a specific mock."""
        return self.mocks.get(name)


# Constants for test data
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
BATCH_SIZE = 32

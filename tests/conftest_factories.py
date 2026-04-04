"""
Common test data factories and fixtures for the test suite.
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Provide a sample configuration for tests."""
    return {
        "timeout": 30,
        "retries": 3,
        "debug": False,
        "paths": {
            "data": "/tmp/test_data",
            "logs": "/tmp/test_logs"
        }
    }


@pytest.fixture
def mock_agent():
    """Provide a mock agent for tests."""
    agent = Mock()
    agent.execute.return_value = {"status": "success", "result": "test_result"}
    agent.name = "TestAgent"
    agent.version = "1.0.0"
    return agent


@pytest.fixture
def sample_test_data():
    """Provide sample test data."""
    return {
        "test_cases": [
            {"input": "test1", "expected": "result1"},
            {"input": "test2", "expected": "result2"},
            {"input": "test3", "expected": "result3"}
        ],
        "metadata": {
            "version": "1.0",
            "created": "2024-01-01"
        }
    }


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_test_file(path: Path, content: str = "test content"):
        """Create a test file with given content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    @staticmethod
    def create_json_file(path: Path, data: dict[Any, Any]):
        """Create a JSON test file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        return path

    @staticmethod
    def create_mock_response(status: str = "success", data: dict = None):
        """Create a mock response object."""
        response = Mock()
        response.status_code = 200 if status == "success" else 400
        response.json.return_value = data or {"status": status}
        response.text = json.dumps(data or {"status": status})
        return response

    @staticmethod
    def create_test_agent(name: str = "TestAgent", capabilities: list[str] = None):
        """Create a test agent with specified capabilities."""
        agent = Mock()
        agent.name = name
        agent.capabilities = capabilities or ["test_capability"]
        agent.execute.return_value = {"status": "success", "agent": name}
        return agent


# Test utilities
def assert_file_exists(path: Path, message: str = None):
    """Assert that a file exists."""
    assert path.exists(), message or f"File should exist: {path}"


def assert_file_not_exists(path: Path, message: str = None):
    """Assert that a file does not exist."""
    assert not path.exists(), message or f"File should not exist: {path}"


def assert_file_content(path: Path, expected_content: str, message: str = None):
    """Assert that a file has expected content."""
    assert_file_exists(path)
    actual_content = path.read_text()
    assert actual_content == expected_content, message or f"File content mismatch in {path}"


def assert_mock_called(mock: Mock, call_count: int = 1, message: str = None):
    """Assert that a mock was called expected number of times."""
    assert mock.call_count == call_count, message or f"Mock called {mock.call_count} times, expected {call_count}"


# Common test scenarios
def create_test_scenario(name: str, **kwargs):
    """Create a test scenario with common setup."""
    scenario = {
        "name": name,
        "setup": kwargs.get("setup", {}),
        "expected": kwargs.get("expected", {}),
        "mocks": kwargs.get("mocks", {}),
    }
    return scenario

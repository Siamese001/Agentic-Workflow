"""
Unit tests for Testing Utilities.

Tests Phase 4A - Core Testing Framework.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.fixtures.testing_utils import (
    MockFactory,
    TestContext,
    TestDataGenerator,
    TestRunner,
    assert_agent_result_failure,
    assert_agent_result_success,
    create_temp_config_file,
    mock_core_integrity,
    temp_directory,
    temp_env_vars,
)


class TestMockFactory:
    """Test MockFactory functionality."""

    def test_create_agent_mock(self):
        """Test creating an agent mock."""
        mock = MockFactory.create_agent_mock(
            name="test-agent",
            version="2.0.0",
            execute_result={"status": "success"},
        )

        assert mock.name == "test-agent"
        assert mock.version == "2.0.0"
        assert mock.execute.return_value == {"status": "success"}

    def test_create_redis_mock(self):
        """Test creating a Redis mock."""
        mock = MockFactory.create_redis_mock(
            get_return="cached_value",
            set_return=True,
        )

        assert mock.get.return_value == "cached_value"
        assert mock.set.return_value is True
        assert mock.ping.return_value is True

    def test_create_pinecone_mock(self):
        """Test creating a Pinecone mock."""
        mock_results = [MagicMock(id="1", score=0.9)]
        mock = MockFactory.create_pinecone_mock(query_results=mock_results)

        index = mock.Index.return_value
        assert index.query.return_value.matches == mock_results

    def test_create_llm_response_mock(self):
        """Test creating an LLM response mock."""
        mock = MockFactory.create_llm_response_mock(
            content="Hello world",
            model="gpt-4",
        )

        assert mock.content == "Hello world"
        assert mock.model == "gpt-4"
        assert mock.usage.total_tokens == 30


class TestTestDataGenerator:
    """Test TestDataGenerator functionality."""

    def test_generate_profile_data(self):
        """Test generating profile data."""
        data = TestDataGenerator.generate_profile_data(
            name="John Doe",
            email="john@example.com",
            title="Senior Engineer",
        )

        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["title"] == "Senior Engineer"
        assert "skills" in data

    def test_generate_job_data(self):
        """Test generating job data."""
        data = TestDataGenerator.generate_job_data(
            title="Data Scientist",
            company="AI Corp",
        )

        assert data["title"] == "Data Scientist"
        assert data["company"] == "AI Corp"
        assert "requirements" in data

    def test_generate_message_template(self):
        """Test generating message template."""
        data = TestDataGenerator.generate_message_template(
            template_id="outreach-1",
            content="Hi {name}, interested in {role}?",
        )

        assert data["id"] == "outreach-1"
        assert "{name}" in data["content"]

    def test_generate_resume_data(self):
        """Test generating resume data."""
        data = TestDataGenerator.generate_resume_data(name="Jane Smith")

        assert data["name"] == "Jane Smith"
        assert "experience" in data
        assert "education" in data
        assert "skills" in data


class TestTempDirectory:
    """Test temp_directory context manager."""

    def test_creates_directory(self):
        """Test that temp directory is created."""
        with temp_directory() as tmpdir:
            assert tmpdir.exists()
            assert tmpdir.is_dir()

    def test_cleanup_after_exit(self):
        """Test that temp directory is cleaned up."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            saved_path = tmpdir

        assert not saved_path.exists()


class TestTempEnvVars:
    """Test temp_env_vars context manager."""

    def test_sets_env_vars(self):
        """Test that env vars are set."""
        original = os.environ.get("TEST_VAR_123")

        with temp_env_vars(TEST_VAR_123="test_value"):
            assert os.environ.get("TEST_VAR_123") == "test_value"

        # Should be restored
        assert os.environ.get("TEST_VAR_123") == original

    def test_restores_original_values(self):
        """Test that original values are restored."""
        os.environ["EXISTING_VAR"] = "original"

        with temp_env_vars(EXISTING_VAR="temporary"):
            assert os.environ["EXISTING_VAR"] == "temporary"

        assert os.environ["EXISTING_VAR"] == "original"

        # Cleanup
        del os.environ["EXISTING_VAR"]


class TestMockCoreIntegrity:
    """Test mock_core_integrity context manager."""

    def test_provides_mock(self):
        """Test that context manager provides a mock."""
        with mock_core_integrity() as mock:
            assert mock is not None
            assert isinstance(mock, MagicMock)


class TestCreateTempConfigFile:
    """Test create_temp_config_file function."""

    def test_creates_json_file(self):
        """Test creating a JSON config file."""
        with temp_directory() as tmpdir:
            config_data = {"key": "value", "nested": {"a": 1}}
            filepath = create_temp_config_file(config_data, "test.json", tmpdir)

            assert filepath.exists()
            assert filepath.suffix == ".json"

            import json

            with open(filepath) as f:
                loaded = json.load(f)
            assert loaded == config_data


class TestAssertAgentResult:
    """Test agent result assertion helpers."""

    def test_assert_success_passes(self):
        """Test assert_agent_result_success with successful result."""
        result = MagicMock()
        result.is_success = True

        assert_agent_result_success(result)  # Should not raise

    def test_assert_success_fails(self):
        """Test assert_agent_result_success with failed result."""
        result = MagicMock()
        result.is_success = False
        result.error = "Something failed"

        with pytest.raises(AssertionError):
            assert_agent_result_success(result)

    def test_assert_failure_passes(self):
        """Test assert_agent_result_failure with failed result."""
        result = MagicMock()
        result.is_failure = True
        result.error = "Expected error message"

        assert_agent_result_failure(result, "Expected error")  # Should not raise

    def test_assert_failure_fails(self):
        """Test assert_agent_result_failure with successful result."""
        result = MagicMock()
        result.is_failure = False

        with pytest.raises(AssertionError):
            assert_agent_result_failure(result)


class TestTestContext:
    """Test TestContext dataclass."""

    def test_context_creation(self):
        """Test creating a test context."""
        context = TestContext(
            test_name="test_example",
            env_vars={"KEY": "VALUE"},
        )

        assert context.test_name == "test_example"
        assert context.env_vars == {"KEY": "VALUE"}
        assert context.temp_dir is None
        assert context.mock_objects == {}


class TestTestRunner:
    """Test TestRunner functionality."""

    def test_runner_initialization(self):
        """Test TestRunner initialization."""
        runner = TestRunner(test_dir=Path("tests/unit"))
        assert runner.test_dir == Path("tests/unit")
        assert runner.results == []

    def test_get_test_summary_empty(self):
        """Test getting summary with no results."""
        runner = TestRunner()
        summary = runner.get_test_summary()

        assert summary["total_runs"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0

    def test_get_test_summary_with_results(self):
        """Test getting summary with results."""
        runner = TestRunner()
        runner.results = [
            {"success": True},
            {"success": True},
            {"success": False},
        ]

        summary = runner.get_test_summary()

        assert summary["total_runs"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1

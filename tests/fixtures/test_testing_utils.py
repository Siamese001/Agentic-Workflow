"""
Core Testing Utilities - Shared fixtures and helpers for testing.

Provides mock factories, test data generators, and common test utilities
for apps_lic and apps_rg testing.
Phase 4A - Core Testing Framework
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch


@dataclass
class MockConfig:
    """Configuration for mock objects."""

    return_value: Any = None
    side_effect: Any = None
    raise_exception: Exception | None = None


@dataclass
class TestContext:
    """Context for test execution."""

    test_name: str
    temp_dir: Path | None = None
    env_vars: dict[str, str] = field(default_factory=dict)
    mock_objects: dict[str, MagicMock] = field(default_factory=dict)


class MockFactory:
    """Factory for creating mock objects."""

    @staticmethod
    def create_agent_mock(
        name: str = "test-agent",
        version: str = "1.0.0",
        execute_result: Any = None,
    ) -> MagicMock:
        """Create a mock agent."""
        mock = MagicMock()
        mock.name = name
        mock.version = version
        mock.execute.return_value = execute_result
        return mock

    @staticmethod
    def create_redis_mock(
        get_return: Any = None,
        set_return: bool = True,
    ) -> MagicMock:
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.get.return_value = get_return
        mock.set.return_value = set_return
        mock.setex.return_value = set_return
        mock.delete.return_value = 1
        mock.ping.return_value = True
        mock.scan.return_value = (0, [])
        return mock

    @staticmethod
    def create_pinecone_mock(
        query_results: list | None = None,
    ) -> MagicMock:
        """Create a mock Pinecone client."""
        mock = MagicMock()
        mock.list_indexes.return_value.names.return_value = ["test-index"]

        mock_index = MagicMock()
        if query_results:
            mock_index.query.return_value.matches = query_results
        else:
            mock_index.query.return_value.matches = []

        mock.Index.return_value = mock_index
        return mock

    @staticmethod
    def create_llm_response_mock(
        content: str = "Test response",
        model: str = "test-model",
    ) -> MagicMock:
        """Create a mock LLM response."""
        mock = MagicMock()
        mock.content = content
        mock.model = model
        mock.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        return mock


class TestDataGenerator:
    """Generator for test data."""

    @staticmethod
    def generate_profile_data(
        name: str = "Test User",
        email: str = "test@example.com",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate profile test data."""
        return {
            "name": name,
            "email": email,
            "title": kwargs.get("title", "Software Engineer"),
            "company": kwargs.get("company", "Test Company"),
            "skills": kwargs.get("skills", ["Python", "JavaScript"]),
            "experience_years": kwargs.get("experience_years", 5),
        }

    @staticmethod
    def generate_job_data(
        title: str = "Software Engineer",
        company: str = "Tech Corp",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate job posting test data."""
        return {
            "title": title,
            "company": company,
            "description": kwargs.get("description", "A great opportunity..."),
            "requirements": kwargs.get("requirements", ["Python", "3+ years"]),
            "location": kwargs.get("location", "Remote"),
            "salary_range": kwargs.get("salary_range", "$100k-$150k"),
        }

    @staticmethod
    def generate_message_template(
        template_id: str = "test-template",
        content: str = "Hello {name}, ...",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate message template test data."""
        return {
            "id": template_id,
            "content": content,
            "subject": kwargs.get("subject", "Test Subject"),
            "variables": kwargs.get("variables", ["name"]),
            "category": kwargs.get("category", "outreach"),
        }

    @staticmethod
    def generate_resume_data(
        name: str = "Test User",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate resume test data."""
        return {
            "name": name,
            "email": kwargs.get("email", "test@example.com"),
            "phone": kwargs.get("phone", "555-1234"),
            "summary": kwargs.get("summary", "Experienced professional..."),
            "experience": kwargs.get(
                "experience",
                [
                    {
                        "title": "Senior Developer",
                        "company": "Tech Inc",
                        "duration": "2020-2024",
                    },
                ],
            ),
            "education": kwargs.get(
                "education",
                [{"degree": "BS Computer Science", "school": "Test University"}],
            ),
            "skills": kwargs.get("skills", ["Python", "AWS", "Docker"]),
        }


@contextmanager
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@contextmanager
def temp_env_vars(**env_vars: str) -> Generator[None, None, None]:
    """Temporarily set environment variables."""
    original = {}
    for key, value in env_vars.items():
        original[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        yield
    finally:
        for key, orig_value in original.items():
            if orig_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = orig_value


@contextmanager
def mock_core_integrity() -> Generator[MagicMock, None, None]:
    """Mock CoreIntegrityVerifier for testing agents."""
    mock_path = "agentic_core.L0_maintenance.enforcement.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity"
    with patch(mock_path) as mock:
        yield mock


def create_temp_config_file(
    config_data: dict[str, Any],
    filename: str = "config.json",
    directory: Path | None = None,
) -> Path:
    """Create a temporary configuration file."""
    if directory is None:
        directory = Path(tempfile.gettempdir())

    filepath = directory / filename
    with open(filepath, "w") as f:
        json.dump(config_data, f)

    return filepath


def assert_agent_result_success(result: Any) -> None:
    """Assert that an agent result is successful."""
    assert hasattr(result, "is_success"), "Result must have is_success property"
    assert result.is_success, f"Expected success but got: {result.error}"


def assert_agent_result_failure(result: Any, expected_error: str | None = None) -> None:
    """Assert that an agent result is a failure."""
    assert hasattr(result, "is_failure"), "Result must have is_failure property"
    assert result.is_failure, "Expected failure but got success"
    if expected_error:
        assert expected_error in result.error, f"Expected '{expected_error}' in error"


class TestRunner:
    """Helper for running test suites programmatically."""

    def __init__(self, test_dir: Path | None = None):
        self.test_dir = test_dir or Path("tests")
        self.results: list[dict[str, Any]] = []

    def run_tests(
        self,
        pattern: str = "test_*.py",
        verbose: bool = False,
    ) -> dict[str, Any]:
        """Run tests matching the pattern."""
        import subprocess

        cmd = ["python", "-m", "pytest", str(self.test_dir), "-v" if verbose else "-q"]

        if pattern != "test_*.py":
            cmd.extend(["-k", pattern])

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def get_test_summary(self) -> dict[str, Any]:
        """Get summary of test results."""
        return {
            "total_runs": len(self.results),
            "passed": sum(1 for r in self.results if r.get("success")),
            "failed": sum(1 for r in self.results if not r.get("success")),
        }

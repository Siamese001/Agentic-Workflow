import subprocess
import pytest


@pytest.mark.mock
def test_no_todo_or_mock_comments():
    result = subprocess.run(["grep", "-R", "TODO", "agentic_workflow/"], capture_output=True, text=True)
    assert "TODO" not in result.stdout


@pytest.mark.mock
def test_no_identity_function_returns():
    result = subprocess.run(["grep", "-R", "return input", "agentic_workflow/"], capture_output=True, text=True)
    assert "return input" not in result.stdout


@pytest.mark.skip("Add 13 more mock detection tests")
def test_placeholder():
    pass

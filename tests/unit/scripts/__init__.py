_logger = logging.getLogger(__name__)
'Unit tests for scripts module.\n\nThis package contains unit tests for the scripts module, including:\n- Logic operations tests\n- Data access functionality tests\n- Synthesis and validation tests\n- Pipeline orchestration tests\n- Runtime execution tests\n\nTest Structure:\n- Each test module corresponds to a specific scripts submodule\n- Tests follow the standard pytest conventions\n- Mock objects and fixtures are provided for complex dependencies\n'
import logging
import pytest
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_script_context() -> None:
    """Provide a mock script context for testing."""
    return {'runtime': 'test', 'environment': 'unit_test', 'debug': True}
__all__ = ['mock_script_context']
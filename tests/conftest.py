# Core pytest configuration
import pytest


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path

    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"


# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")


"""Root conftest — suppress lifecycle trace logging during test collection and execution."""
import logging
from pathlib import Path

import pytest  # noqa: E402

# NOTE: Disabled imports due to collection-time import conflicts
# Tests needing these fixtures should import directly
# try:
#     from .conftest_factories import *
# except ImportError:
#     pass
#
# try:
#     from .conftest_isolation import (
#         temp_directory,
#         isolated_cwd,
#         clean_env,
#         IsolatedTest,
#         capture_global_state,
#         restore_global_state,
#     )
# except ImportError:
#     pass

# Suppress lifecycle trace loggers that emit ~100K lines during import/execution.
# These overwhelm pytest's capture system causing OSError: Bad file descriptor.
for _name in ["adg", "lifecycle"]:
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False


# NOTE: cached_adg_scan fixture removed due to import conflicts during full collection.
# Tests needing ADG scan should import ADGStaticScanner directly or use test-local fixtures.


# Shared fixtures for test reconstruction
@pytest.fixture
def mock_config():
    """Mock configuration fixture."""
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def mock_agent():
    """Mock agent fixture."""
    from unittest.mock import Mock

    agent = Mock()
    agent.id = "test-agent-001"
    agent.state = "idle"
    return agent


# Common test constants
TEST_CONFIG = {"batch_size": 32, "timeout": 30, "max_retries": 3}

TEST_AGENT_CONFIG = {"id": "test-agent-001", "type": "test", "state": "idle"}

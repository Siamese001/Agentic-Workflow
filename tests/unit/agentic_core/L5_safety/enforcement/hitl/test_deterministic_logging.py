"""Test DeterministicLogging functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterministicLogging:
    """Test DeterministicLogging functionality."""

    def test_deterministic_logging_imports(self):
        """Test deterministic_logging module imports."""
        from agentic_core import deterministic_logging

        assert deterministic_logging is not None

    def test_deterministic_logging_class(self):
        """Test DeterministicLogging class exists."""
        from agentic_core import DeterministicLogging

        assert DeterministicLogging is not None

    def test_deterministic_logging_callable(self):
        """Test deterministic_logging functions are callable."""
        from agentic_core import validate_deterministic_logging

        assert callable(validate_deterministic_logging)

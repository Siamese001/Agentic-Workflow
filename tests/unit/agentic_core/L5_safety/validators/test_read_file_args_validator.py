"""Test ReadFileArgsValidator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReadFileArgsValidator:
    """Test ReadFileArgsValidator functionality."""

    def test_read_file_args_validator_imports(self):
        """Test read_file_args_validator module imports."""
        from agentic_core import read_file_args_validator

        assert read_file_args_validator is not None

    def test_read_file_args_validator_class(self):
        """Test ReadFileArgsValidator class exists."""
        from agentic_core import ReadFileArgsValidator

        assert ReadFileArgsValidator is not None

    def test_read_file_args_validator_callable(self):
        """Test read_file_args_validator functions are callable."""
        from agentic_core import validate_read_file_args_validator

        assert callable(validate_read_file_args_validator)

"""Test CodeValidatorRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeValidatorRunnerAdg:
    """Test CodeValidatorRunnerAdg functionality."""

    def test_code_validator_runner_adg_imports(self):
        """Test code_validator_runner_adg module imports."""
        from agentic_core import code_validator_runner_adg

        assert code_validator_runner_adg is not None

    def test_code_validator_runner_adg_class(self):
        """Test CodeValidatorRunnerAdg class exists."""
        from agentic_core import CodeValidatorRunnerAdg

        assert CodeValidatorRunnerAdg is not None

    def test_code_validator_runner_adg_callable(self):
        """Test code_validator_runner_adg functions are callable."""
        from agentic_core import validate_code_validator_runner_adg

        assert callable(validate_code_validator_runner_adg)

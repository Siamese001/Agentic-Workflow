"""Test GoldenStateCaseValidator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGoldenStateCaseValidator:
    """Test GoldenStateCaseValidator functionality."""

    def test_golden_state_case_validator_imports(self):
        """Test golden_state_case_validator module imports."""
        from agentic_core import golden_state_case_validator

        assert golden_state_case_validator is not None

    def test_golden_state_case_validator_class(self):
        """Test GoldenStateCaseValidator class exists."""
        from agentic_core import GoldenStateCaseValidator

        assert GoldenStateCaseValidator is not None

    def test_golden_state_case_validator_callable(self):
        """Test golden_state_case_validator functions are callable."""
        from agentic_core import validate_golden_state_case_validator

        assert callable(validate_golden_state_case_validator)

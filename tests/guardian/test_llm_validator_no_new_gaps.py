"""Test LlmValidatorNoNewGaps functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmValidatorNoNewGaps:
    """Test LlmValidatorNoNewGaps functionality."""

    def test_llm_validator_no_new_gaps_imports(self):
        """Test llm_validator_no_new_gaps module imports."""
        from agentic_core import llm_validator_no_new_gaps
        assert llm_validator_no_new_gaps is not None

    def test_llm_validator_no_new_gaps_class(self):
        """Test LlmValidatorNoNewGaps class exists."""
        from agentic_core import LlmValidatorNoNewGaps
        assert LlmValidatorNoNewGaps is not None

    def test_llm_validator_no_new_gaps_callable(self):
        """Test llm_validator_no_new_gaps functions are callable."""
        from agentic_core import validate_llm_validator_no_new_gaps
        assert callable(validate_llm_validator_no_new_gaps)

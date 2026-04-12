"""Test FileClassificationValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFileClassificationValidatorAdg:
    """Test FileClassificationValidatorAdg functionality."""

    def test_file_classification_validator_adg_imports(self):
        """Test file_classification_validator_adg module imports."""
        from agentic_core import file_classification_validator_adg

        assert file_classification_validator_adg is not None

    def test_file_classification_validator_adg_class(self):
        """Test FileClassificationValidatorAdg class exists."""
        from agentic_core import FileClassificationValidatorAdg

        assert FileClassificationValidatorAdg is not None

    def test_file_classification_validator_adg_callable(self):
        """Test file_classification_validator_adg functions are callable."""
        from agentic_core import validate_file_classification_validator_adg

        assert callable(validate_file_classification_validator_adg)

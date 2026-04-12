"""Test ValidatorClassificationPrecision functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidatorClassificationPrecision:
    """Test ValidatorClassificationPrecision functionality."""

    def test_validator_classification_precision_imports(self):
        """Test validator_classification_precision module imports."""
        from agentic_core import validator_classification_precision

        assert validator_classification_precision is not None

    def test_validator_classification_precision_class(self):
        """Test ValidatorClassificationPrecision class exists."""
        from agentic_core import ValidatorClassificationPrecision

        assert ValidatorClassificationPrecision is not None

    def test_validator_classification_precision_callable(self):
        """Test validator_classification_precision functions are callable."""
        from agentic_core import validate_validator_classification_precision

        assert callable(validate_validator_classification_precision)

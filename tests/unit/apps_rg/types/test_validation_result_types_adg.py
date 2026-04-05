"""Test ValidationResultTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidationResultTypesAdg:
    """Test ValidationResultTypesAdg functionality."""

    def test_validation_result_types_adg_imports(self):
        """Test validation_result_types_adg module imports."""
        from agentic_core import validation_result_types_adg
        assert validation_result_types_adg is not None

    def test_validation_result_types_adg_class(self):
        """Test ValidationResultTypesAdg class exists."""
        from agentic_core import ValidationResultTypesAdg
        assert ValidationResultTypesAdg is not None

    def test_validation_result_types_adg_callable(self):
        """Test validation_result_types_adg functions are callable."""
        from agentic_core import validate_validation_result_types_adg
        assert callable(validate_validation_result_types_adg)

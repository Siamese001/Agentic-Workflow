"""Test IntegrityValidationTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIntegrityValidationTypesAdg:
    """Test IntegrityValidationTypesAdg functionality."""

    def test_integrity_validation_types_adg_imports(self):
        """Test integrity_validation_types_adg module imports."""
        from agentic_core import integrity_validation_types_adg

        assert integrity_validation_types_adg is not None

    def test_integrity_validation_types_adg_class(self):
        """Test IntegrityValidationTypesAdg class exists."""
        from agentic_core import IntegrityValidationTypesAdg

        assert IntegrityValidationTypesAdg is not None

    def test_integrity_validation_types_adg_callable(self):
        """Test integrity_validation_types_adg functions are callable."""
        from agentic_core import validate_integrity_validation_types_adg

        assert callable(validate_integrity_validation_types_adg)

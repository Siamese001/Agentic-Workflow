"""Test GuardianClassificationCompliance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianClassificationCompliance:
    """Test GuardianClassificationCompliance functionality."""

    def test_guardian_classification_compliance_imports(self):
        """Test guardian_classification_compliance module imports."""
        from agentic_core import guardian_classification_compliance
        assert guardian_classification_compliance is not None

    def test_guardian_classification_compliance_class(self):
        """Test GuardianClassificationCompliance class exists."""
        from agentic_core import GuardianClassificationCompliance
        assert GuardianClassificationCompliance is not None

    def test_guardian_classification_compliance_callable(self):
        """Test guardian_classification_compliance functions are callable."""
        from agentic_core import validate_guardian_classification_compliance
        assert callable(validate_guardian_classification_compliance)

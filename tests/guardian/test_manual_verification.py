"""Test ManualVerification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestManualVerification:
    """Test ManualVerification functionality."""

    def test_manual_verification_imports(self):
        """Test manual_verification module imports."""
        from agentic_core import manual_verification
        assert manual_verification is not None

    def test_manual_verification_class(self):
        """Test ManualVerification class exists."""
        from agentic_core import ManualVerification
        assert ManualVerification is not None

    def test_manual_verification_callable(self):
        """Test manual_verification functions are callable."""
        from agentic_core import validate_manual_verification
        assert callable(validate_manual_verification)

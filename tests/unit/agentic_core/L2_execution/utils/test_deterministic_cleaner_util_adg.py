"""Test DeterministicCleanerUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterministicCleanerUtilAdg:
    """Test DeterministicCleanerUtilAdg functionality."""

    def test_deterministic_cleaner_util_adg_imports(self):
        """Test deterministic_cleaner_util_adg module imports."""
        from agentic_core import deterministic_cleaner_util_adg

        assert deterministic_cleaner_util_adg is not None

    def test_deterministic_cleaner_util_adg_class(self):
        """Test DeterministicCleanerUtilAdg class exists."""
        from agentic_core import DeterministicCleanerUtilAdg

        assert DeterministicCleanerUtilAdg is not None

    def test_deterministic_cleaner_util_adg_callable(self):
        """Test deterministic_cleaner_util_adg functions are callable."""
        from agentic_core import validate_deterministic_cleaner_util_adg

        assert callable(validate_deterministic_cleaner_util_adg)

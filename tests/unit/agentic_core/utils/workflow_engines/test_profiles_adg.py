"""Test ProfilesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProfilesAdg:
    """Test ProfilesAdg functionality."""

    def test_profiles_adg_imports(self):
        """Test profiles_adg module imports."""
        from agentic_core import profiles_adg

        assert profiles_adg is not None

    def test_profiles_adg_class(self):
        """Test ProfilesAdg class exists."""
        from agentic_core import ProfilesAdg

        assert ProfilesAdg is not None

    def test_profiles_adg_callable(self):
        """Test profiles_adg functions are callable."""
        from agentic_core import validate_profiles_adg

        assert callable(validate_profiles_adg)

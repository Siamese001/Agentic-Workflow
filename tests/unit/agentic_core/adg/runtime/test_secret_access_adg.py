"""Test SecretAccessAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSecretAccessAdg:
    """Test SecretAccessAdg functionality."""

    def test_secret_access_adg_imports(self):
        """Test secret_access_adg module imports."""
        from agentic_core import secret_access_adg

        assert secret_access_adg is not None

    def test_secret_access_adg_class(self):
        """Test SecretAccessAdg class exists."""
        from agentic_core import SecretAccessAdg

        assert SecretAccessAdg is not None

    def test_secret_access_adg_callable(self):
        """Test secret_access_adg functions are callable."""
        from agentic_core import validate_secret_access_adg

        assert callable(validate_secret_access_adg)

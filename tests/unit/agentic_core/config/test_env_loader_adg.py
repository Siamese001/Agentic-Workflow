"""Test EnvLoaderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEnvLoaderAdg:
    """Test EnvLoaderAdg functionality."""

    def test_env_loader_adg_imports(self):
        """Test env_loader_adg module imports."""
        from agentic_core import env_loader_adg

        assert env_loader_adg is not None

    def test_env_loader_adg_class(self):
        """Test EnvLoaderAdg class exists."""
        from agentic_core import EnvLoaderAdg

        assert EnvLoaderAdg is not None

    def test_env_loader_adg_callable(self):
        """Test env_loader_adg functions are callable."""
        from agentic_core import validate_env_loader_adg

        assert callable(validate_env_loader_adg)

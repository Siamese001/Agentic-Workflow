"""Test SsotCli functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotCli:
    """Test SsotCli functionality."""

    def test_ssot_cli_imports(self):
        """Test ssot_cli module imports."""
        from agentic_core import ssot_cli

        assert ssot_cli is not None

    def test_ssot_cli_class(self):
        """Test SsotCli class exists."""
        from agentic_core import SsotCli

        assert SsotCli is not None

    def test_ssot_cli_callable(self):
        """Test ssot_cli functions are callable."""
        from agentic_core import validate_ssot_cli

        assert callable(validate_ssot_cli)

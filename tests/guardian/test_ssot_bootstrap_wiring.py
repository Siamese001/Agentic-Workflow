"""Test SsotBootstrapWiring functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotBootstrapWiring:
    """Test SsotBootstrapWiring functionality."""

    def test_ssot_bootstrap_wiring_imports(self):
        """Test ssot_bootstrap_wiring module imports."""
        from agentic_core import ssot_bootstrap_wiring
        assert ssot_bootstrap_wiring is not None

    def test_ssot_bootstrap_wiring_class(self):
        """Test SsotBootstrapWiring class exists."""
        from agentic_core import SsotBootstrapWiring
        assert SsotBootstrapWiring is not None

    def test_ssot_bootstrap_wiring_callable(self):
        """Test ssot_bootstrap_wiring functions are callable."""
        from agentic_core import validate_ssot_bootstrap_wiring
        assert callable(validate_ssot_bootstrap_wiring)

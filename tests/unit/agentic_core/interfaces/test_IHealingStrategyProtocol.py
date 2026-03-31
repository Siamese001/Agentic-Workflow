"""Test Ihealingstrategyprotocol functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIhealingstrategyprotocol:
    """Test Ihealingstrategyprotocol functionality."""

    def test_IHealingStrategyProtocol_imports(self):
        """Test IHealingStrategyProtocol module imports."""
        from agentic_core import IHealingStrategyProtocol
        assert IHealingStrategyProtocol is not None

    def test_IHealingStrategyProtocol_class(self):
        """Test Ihealingstrategyprotocol class exists."""
        from agentic_core import Ihealingstrategyprotocol
        assert Ihealingstrategyprotocol is not None

    def test_IHealingStrategyProtocol_callable(self):
        """Test IHealingStrategyProtocol functions are callable."""
        from agentic_core import validate_IHealingStrategyProtocol
        assert callable(validate_IHealingStrategyProtocol)

"""Test ProposerBridgeAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProposerBridgeAdg:
    """Test ProposerBridgeAdg functionality."""

    def test_proposer_bridge_adg_imports(self):
        """Test proposer_bridge_adg module imports."""
        from agentic_core import proposer_bridge_adg

        assert proposer_bridge_adg is not None

    def test_proposer_bridge_adg_class(self):
        """Test ProposerBridgeAdg class exists."""
        from agentic_core import ProposerBridgeAdg

        assert ProposerBridgeAdg is not None

    def test_proposer_bridge_adg_callable(self):
        """Test proposer_bridge_adg functions are callable."""
        from agentic_core import validate_proposer_bridge_adg

        assert callable(validate_proposer_bridge_adg)

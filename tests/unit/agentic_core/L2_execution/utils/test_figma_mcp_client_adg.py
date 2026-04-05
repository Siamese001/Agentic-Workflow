"""Test FigmaMcpClientAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFigmaMcpClientAdg:
    """Test FigmaMcpClientAdg functionality."""

    def test_figma_mcp_client_adg_imports(self):
        """Test figma_mcp_client_adg module imports."""
        from agentic_core import figma_mcp_client_adg
        assert figma_mcp_client_adg is not None

    def test_figma_mcp_client_adg_class(self):
        """Test FigmaMcpClientAdg class exists."""
        from agentic_core import FigmaMcpClientAdg
        assert FigmaMcpClientAdg is not None

    def test_figma_mcp_client_adg_callable(self):
        """Test figma_mcp_client_adg functions are callable."""
        from agentic_core import validate_figma_mcp_client_adg
        assert callable(validate_figma_mcp_client_adg)

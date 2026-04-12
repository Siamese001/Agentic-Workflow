"""Test UnifiedAgentPerformance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestUnifiedAgentPerformance:
    """Test UnifiedAgentPerformance functionality."""

    def test_unified_agent_performance_imports(self):
        """Test unified_agent_performance module imports."""
        from agentic_core import unified_agent_performance

        assert unified_agent_performance is not None

    def test_unified_agent_performance_class(self):
        """Test UnifiedAgentPerformance class exists."""
        from agentic_core import UnifiedAgentPerformance

        assert UnifiedAgentPerformance is not None

    def test_unified_agent_performance_callable(self):
        """Test unified_agent_performance functions are callable."""
        from agentic_core import validate_unified_agent_performance

        assert callable(validate_unified_agent_performance)

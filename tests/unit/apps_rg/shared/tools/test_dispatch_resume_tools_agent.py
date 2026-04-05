"""Test DispatchResumeToolsAgent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDispatchResumeToolsAgent:
    """Test DispatchResumeToolsAgent functionality."""

    def test_dispatch_resume_tools_agent_imports(self):
        """Test dispatch_resume_tools_agent module imports."""
        from agentic_core import dispatch_resume_tools_agent
        assert dispatch_resume_tools_agent is not None

    def test_dispatch_resume_tools_agent_class(self):
        """Test DispatchResumeToolsAgent class exists."""
        from agentic_core import DispatchResumeToolsAgent
        assert DispatchResumeToolsAgent is not None

    def test_dispatch_resume_tools_agent_callable(self):
        """Test dispatch_resume_tools_agent functions are callable."""
        from agentic_core import validate_dispatch_resume_tools_agent
        assert callable(validate_dispatch_resume_tools_agent)

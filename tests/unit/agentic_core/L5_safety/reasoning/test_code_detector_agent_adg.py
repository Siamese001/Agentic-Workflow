"""Test CodeDetectorAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeDetectorAgentAdg:
    """Test CodeDetectorAgentAdg functionality."""

    def test_code_detector_agent_adg_imports(self):
        """Test code_detector_agent_adg module imports."""
        from agentic_core import code_detector_agent_adg

        assert code_detector_agent_adg is not None

    def test_code_detector_agent_adg_class(self):
        """Test CodeDetectorAgentAdg class exists."""
        from agentic_core import CodeDetectorAgentAdg

        assert CodeDetectorAgentAdg is not None

    def test_code_detector_agent_adg_callable(self):
        """Test code_detector_agent_adg functions are callable."""
        from agentic_core import validate_code_detector_agent_adg

        assert callable(validate_code_detector_agent_adg)

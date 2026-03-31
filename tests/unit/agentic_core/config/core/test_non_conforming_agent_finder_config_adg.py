"""Test NonConformingAgentFinderConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNonConformingAgentFinderConfigAdg:
    """Test NonConformingAgentFinderConfigAdg functionality."""

    def test_non_conforming_agent_finder_config_adg_imports(self):
        """Test non_conforming_agent_finder_config_adg module imports."""
        from agentic_core import non_conforming_agent_finder_config_adg
        assert non_conforming_agent_finder_config_adg is not None

    def test_non_conforming_agent_finder_config_adg_class(self):
        """Test NonConformingAgentFinderConfigAdg class exists."""
        from agentic_core import NonConformingAgentFinderConfigAdg
        assert NonConformingAgentFinderConfigAdg is not None

    def test_non_conforming_agent_finder_config_adg_callable(self):
        """Test non_conforming_agent_finder_config_adg functions are callable."""
        from agentic_core import validate_non_conforming_agent_finder_config_adg
        assert callable(validate_non_conforming_agent_finder_config_adg)

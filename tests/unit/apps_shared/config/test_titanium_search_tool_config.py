"""Test TitaniumSearchToolConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTitaniumSearchToolConfig:
    """Test TitaniumSearchToolConfig functionality."""

    def test_titanium_search_tool_config_imports(self):
        """Test titanium_search_tool_config module imports."""
        from agentic_core import titanium_search_tool_config

        assert titanium_search_tool_config is not None

    def test_titanium_search_tool_config_class(self):
        """Test TitaniumSearchToolConfig class exists."""
        from agentic_core import TitaniumSearchToolConfig

        assert TitaniumSearchToolConfig is not None

    def test_titanium_search_tool_config_callable(self):
        """Test titanium_search_tool_config functions are callable."""
        from agentic_core import validate_titanium_search_tool_config

        assert callable(validate_titanium_search_tool_config)

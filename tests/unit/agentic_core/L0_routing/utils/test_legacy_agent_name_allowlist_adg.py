"""Test LegacyAgentNameAllowlistAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLegacyAgentNameAllowlistAdg:
    """Test LegacyAgentNameAllowlistAdg functionality."""

    def test_legacy_agent_name_allowlist_adg_imports(self):
        """Test legacy_agent_name_allowlist_adg module imports."""
        from agentic_core import legacy_agent_name_allowlist_adg

        assert legacy_agent_name_allowlist_adg is not None

    def test_legacy_agent_name_allowlist_adg_class(self):
        """Test LegacyAgentNameAllowlistAdg class exists."""
        from agentic_core import LegacyAgentNameAllowlistAdg

        assert LegacyAgentNameAllowlistAdg is not None

    def test_legacy_agent_name_allowlist_adg_callable(self):
        """Test legacy_agent_name_allowlist_adg functions are callable."""
        from agentic_core import validate_legacy_agent_name_allowlist_adg

        assert callable(validate_legacy_agent_name_allowlist_adg)

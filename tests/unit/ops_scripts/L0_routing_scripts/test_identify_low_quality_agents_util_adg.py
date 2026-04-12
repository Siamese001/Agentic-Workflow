"""Test IdentifyLowQualityAgentsUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIdentifyLowQualityAgentsUtilAdg:
    """Test IdentifyLowQualityAgentsUtilAdg functionality."""

    def test_identify_low_quality_agents_util_adg_imports(self):
        """Test identify_low_quality_agents_util_adg module imports."""
        from agentic_core import identify_low_quality_agents_util_adg

        assert identify_low_quality_agents_util_adg is not None

    def test_identify_low_quality_agents_util_adg_class(self):
        """Test IdentifyLowQualityAgentsUtilAdg class exists."""
        from agentic_core import IdentifyLowQualityAgentsUtilAdg

        assert IdentifyLowQualityAgentsUtilAdg is not None

    def test_identify_low_quality_agents_util_adg_callable(self):
        """Test identify_low_quality_agents_util_adg functions are callable."""
        from agentic_core import validate_identify_low_quality_agents_util_adg

        assert callable(validate_identify_low_quality_agents_util_adg)

"""Test AppContentValidatorAgentTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppContentValidatorAgentTypesAdg:
    """Test AppContentValidatorAgentTypesAdg functionality."""

    def test_app_content_validator_agent_types_adg_imports(self):
        """Test app_content_validator_agent_types_adg module imports."""
        from agentic_core import app_content_validator_agent_types_adg

        assert app_content_validator_agent_types_adg is not None

    def test_app_content_validator_agent_types_adg_class(self):
        """Test AppContentValidatorAgentTypesAdg class exists."""
        from agentic_core import AppContentValidatorAgentTypesAdg

        assert AppContentValidatorAgentTypesAdg is not None

    def test_app_content_validator_agent_types_adg_callable(self):
        """Test app_content_validator_agent_types_adg functions are callable."""
        from agentic_core import validate_app_content_validator_agent_types_adg

        assert callable(validate_app_content_validator_agent_types_adg)

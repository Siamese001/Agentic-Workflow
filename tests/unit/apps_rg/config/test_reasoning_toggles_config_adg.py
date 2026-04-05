"""Test ReasoningTogglesConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningTogglesConfigAdg:
    """Test ReasoningTogglesConfigAdg functionality."""

    def test_reasoning_toggles_config_adg_imports(self):
        """Test reasoning_toggles_config_adg module imports."""
        from agentic_core import reasoning_toggles_config_adg
        assert reasoning_toggles_config_adg is not None

    def test_reasoning_toggles_config_adg_class(self):
        """Test ReasoningTogglesConfigAdg class exists."""
        from agentic_core import ReasoningTogglesConfigAdg
        assert ReasoningTogglesConfigAdg is not None

    def test_reasoning_toggles_config_adg_callable(self):
        """Test reasoning_toggles_config_adg functions are callable."""
        from agentic_core import validate_reasoning_toggles_config_adg
        assert callable(validate_reasoning_toggles_config_adg)

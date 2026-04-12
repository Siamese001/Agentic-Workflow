"""Test CallPersonalizationApiAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCallPersonalizationApiAdg:
    """Test CallPersonalizationApiAdg functionality."""

    def test_call_personalization_api_adg_imports(self):
        """Test call_personalization_api_adg module imports."""
        from agentic_core import call_personalization_api_adg

        assert call_personalization_api_adg is not None

    def test_call_personalization_api_adg_class(self):
        """Test CallPersonalizationApiAdg class exists."""
        from agentic_core import CallPersonalizationApiAdg

        assert CallPersonalizationApiAdg is not None

    def test_call_personalization_api_adg_callable(self):
        """Test call_personalization_api_adg functions are callable."""
        from agentic_core import validate_call_personalization_api_adg

        assert callable(validate_call_personalization_api_adg)

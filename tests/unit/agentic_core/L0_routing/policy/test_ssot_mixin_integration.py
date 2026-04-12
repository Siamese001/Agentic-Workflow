"""Test SsotMixinIntegration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotMixinIntegration:
    """Test SsotMixinIntegration functionality."""

    def test_ssot_mixin_integration_imports(self):
        """Test ssot_mixin_integration module imports."""
        from agentic_core import ssot_mixin_integration

        assert ssot_mixin_integration is not None

    def test_ssot_mixin_integration_class(self):
        """Test SsotMixinIntegration class exists."""
        from agentic_core import SsotMixinIntegration

        assert SsotMixinIntegration is not None

    def test_ssot_mixin_integration_callable(self):
        """Test ssot_mixin_integration functions are callable."""
        from agentic_core import validate_ssot_mixin_integration

        assert callable(validate_ssot_mixin_integration)

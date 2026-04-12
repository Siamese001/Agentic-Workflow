"""Test InjectionLayerConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInjectionLayerConfigAdg:
    """Test InjectionLayerConfigAdg functionality."""

    def test_injection_layer_config_adg_imports(self):
        """Test injection_layer_config_adg module imports."""
        from agentic_core import injection_layer_config_adg

        assert injection_layer_config_adg is not None

    def test_injection_layer_config_adg_class(self):
        """Test InjectionLayerConfigAdg class exists."""
        from agentic_core import InjectionLayerConfigAdg

        assert InjectionLayerConfigAdg is not None

    def test_injection_layer_config_adg_callable(self):
        """Test injection_layer_config_adg functions are callable."""
        from agentic_core import validate_injection_layer_config_adg

        assert callable(validate_injection_layer_config_adg)

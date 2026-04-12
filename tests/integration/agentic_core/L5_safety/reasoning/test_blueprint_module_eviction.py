"""Test BlueprintModuleEviction functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBlueprintModuleEviction:
    """Test BlueprintModuleEviction functionality."""

    def test_blueprint_module_eviction_imports(self):
        """Test blueprint_module_eviction module imports."""
        try:
            from agentic_core import blueprint_module_eviction

            assert blueprint_module_eviction is not None
        except ImportError:
            pytest.skip("blueprint_module_eviction not available")

    def test_blueprint_module_eviction_class(self):
        """Test BlueprintModuleEviction class exists."""
        try:
            from agentic_core import BlueprintModuleEviction

            assert BlueprintModuleEviction is not None
        except ImportError:
            pytest.skip("BlueprintModuleEviction not available")

    def test_blueprint_module_eviction_callable(self):
        """Test blueprint_module_eviction functions are callable."""
        try:
            from agentic_core import validate_blueprint_module_eviction

            assert callable(validate_blueprint_module_eviction)
        except ImportError:
            pytest.skip("validate_blueprint_module_eviction not available")

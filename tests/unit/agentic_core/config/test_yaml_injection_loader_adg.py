"""Test YamlInjectionLoaderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestYamlInjectionLoaderAdg:
    """Test YamlInjectionLoaderAdg functionality."""

    def test_yaml_injection_loader_adg_imports(self):
        """Test yaml_injection_loader_adg module imports."""
        from agentic_core import yaml_injection_loader_adg

        assert yaml_injection_loader_adg is not None

    def test_yaml_injection_loader_adg_class(self):
        """Test YamlInjectionLoaderAdg class exists."""
        from agentic_core import YamlInjectionLoaderAdg

        assert YamlInjectionLoaderAdg is not None

    def test_yaml_injection_loader_adg_callable(self):
        """Test yaml_injection_loader_adg functions are callable."""
        from agentic_core import validate_yaml_injection_loader_adg

        assert callable(validate_yaml_injection_loader_adg)

"""Test AntipatternRegistryAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAntipatternRegistryAdg:
    """Test AntipatternRegistryAdg functionality."""

    def test_antipattern_registry_adg_imports(self):
        """Test antipattern_registry_adg module imports."""
        from agentic_core import antipattern_registry_adg

        assert antipattern_registry_adg is not None

    def test_antipattern_registry_adg_class(self):
        """Test AntipatternRegistryAdg class exists."""
        from agentic_core import AntipatternRegistryAdg

        assert AntipatternRegistryAdg is not None

    def test_antipattern_registry_adg_callable(self):
        """Test antipattern_registry_adg functions are callable."""
        from agentic_core import validate_antipattern_registry_adg

        assert callable(validate_antipattern_registry_adg)

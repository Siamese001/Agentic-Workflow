"""Test BaseEntityConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBaseEntityConfigAdg:
    """Test BaseEntityConfigAdg functionality."""

    def test_base_entity_config_adg_imports(self):
        """Test base_entity_config_adg module imports."""
        from agentic_core import base_entity_config_adg

        assert base_entity_config_adg is not None

    def test_base_entity_config_adg_class(self):
        """Test BaseEntityConfigAdg class exists."""
        from agentic_core import BaseEntityConfigAdg

        assert BaseEntityConfigAdg is not None

    def test_base_entity_config_adg_callable(self):
        """Test base_entity_config_adg functions are callable."""
        from agentic_core import validate_base_entity_config_adg

        assert callable(validate_base_entity_config_adg)

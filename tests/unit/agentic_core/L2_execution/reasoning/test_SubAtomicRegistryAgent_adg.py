"""Test SubatomicregistryagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSubatomicregistryagentAdg:
    """Test SubatomicregistryagentAdg functionality."""

    def test_SubAtomicRegistryAgent_adg_imports(self):
        """Test SubAtomicRegistryAgent_adg module imports."""
        from agentic_core import SubAtomicRegistryAgent_adg

        assert SubAtomicRegistryAgent_adg is not None

    def test_SubAtomicRegistryAgent_adg_class(self):
        """Test SubatomicregistryagentAdg class exists."""
        from agentic_core import SubatomicregistryagentAdg

        assert SubatomicregistryagentAdg is not None

    def test_SubAtomicRegistryAgent_adg_callable(self):
        """Test SubAtomicRegistryAgent_adg functions are callable."""
        from agentic_core import validate_SubAtomicRegistryAgent_adg

        assert callable(validate_SubAtomicRegistryAgent_adg)

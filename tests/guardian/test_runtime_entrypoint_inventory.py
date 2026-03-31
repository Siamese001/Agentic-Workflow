"""Test RuntimeEntrypointInventory functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeEntrypointInventory:
    """Test RuntimeEntrypointInventory functionality."""

    def test_runtime_entrypoint_inventory_imports(self):
        """Test runtime_entrypoint_inventory module imports."""
        from agentic_core import runtime_entrypoint_inventory
        assert runtime_entrypoint_inventory is not None

    def test_runtime_entrypoint_inventory_class(self):
        """Test RuntimeEntrypointInventory class exists."""
        from agentic_core import RuntimeEntrypointInventory
        assert RuntimeEntrypointInventory is not None

    def test_runtime_entrypoint_inventory_callable(self):
        """Test runtime_entrypoint_inventory functions are callable."""
        from agentic_core import validate_runtime_entrypoint_inventory
        assert callable(validate_runtime_entrypoint_inventory)

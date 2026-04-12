"""Test ResourceManagementTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResourceManagementTypesAdg:
    """Test ResourceManagementTypesAdg functionality."""

    def test_resource_management_types_adg_imports(self):
        """Test resource_management_types_adg module imports."""
        from agentic_core import resource_management_types_adg

        assert resource_management_types_adg is not None

    def test_resource_management_types_adg_class(self):
        """Test ResourceManagementTypesAdg class exists."""
        from agentic_core import ResourceManagementTypesAdg

        assert ResourceManagementTypesAdg is not None

    def test_resource_management_types_adg_callable(self):
        """Test resource_management_types_adg functions are callable."""
        from agentic_core import validate_resource_management_types_adg

        assert callable(validate_resource_management_types_adg)

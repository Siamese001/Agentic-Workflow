"""Test StructuralNamespaceFenceEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructuralNamespaceFenceEnforcer:
    """Test StructuralNamespaceFenceEnforcer functionality."""

    def test_structural_namespace_fence_enforcer_imports(self):
        """Test structural_namespace_fence_enforcer module imports."""
        from agentic_core import structural_namespace_fence_enforcer

        assert structural_namespace_fence_enforcer is not None

    def test_structural_namespace_fence_enforcer_class(self):
        """Test StructuralNamespaceFenceEnforcer class exists."""
        from agentic_core import StructuralNamespaceFenceEnforcer

        assert StructuralNamespaceFenceEnforcer is not None

    def test_structural_namespace_fence_enforcer_callable(self):
        """Test structural_namespace_fence_enforcer functions are callable."""
        from agentic_core import validate_structural_namespace_fence_enforcer

        assert callable(validate_structural_namespace_fence_enforcer)

"""Test MetaInvariantGovernance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaInvariantGovernance:
    """Test MetaInvariantGovernance functionality."""

    def test_meta_invariant_governance_imports(self):
        """Test meta_invariant_governance module imports."""
        from agentic_core import meta_invariant_governance
        assert meta_invariant_governance is not None

    def test_meta_invariant_governance_class(self):
        """Test MetaInvariantGovernance class exists."""
        from agentic_core import MetaInvariantGovernance
        assert MetaInvariantGovernance is not None

    def test_meta_invariant_governance_callable(self):
        """Test meta_invariant_governance functions are callable."""
        from agentic_core import validate_meta_invariant_governance
        assert callable(validate_meta_invariant_governance)

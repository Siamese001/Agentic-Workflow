"""Test MutationTransportAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMutationTransportAdg:
    """Test MutationTransportAdg functionality."""

    def test_mutation_transport_adg_imports(self):
        """Test mutation_transport_adg module imports."""
        from agentic_core import mutation_transport_adg
        assert mutation_transport_adg is not None

    def test_mutation_transport_adg_class(self):
        """Test MutationTransportAdg class exists."""
        from agentic_core import MutationTransportAdg
        assert MutationTransportAdg is not None

    def test_mutation_transport_adg_callable(self):
        """Test mutation_transport_adg functions are callable."""
        from agentic_core import validate_mutation_transport_adg
        assert callable(validate_mutation_transport_adg)

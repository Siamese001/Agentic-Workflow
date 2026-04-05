"""Test C0MutationPrevention functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestC0MutationPrevention:
    """Test C0MutationPrevention functionality."""

    def test_c0_mutation_prevention_imports(self):
        """Test c0_mutation_prevention module imports."""
        from agentic_core import c0_mutation_prevention
        assert c0_mutation_prevention is not None

    def test_c0_mutation_prevention_class(self):
        """Test C0MutationPrevention class exists."""
        from agentic_core import C0MutationPrevention
        assert C0MutationPrevention is not None

    def test_c0_mutation_prevention_callable(self):
        """Test c0_mutation_prevention functions are callable."""
        from agentic_core import validate_c0_mutation_prevention
        assert callable(validate_c0_mutation_prevention)

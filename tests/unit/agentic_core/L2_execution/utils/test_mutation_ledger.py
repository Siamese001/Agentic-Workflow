"""Test MutationLedger functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMutationLedger:
    """Test MutationLedger functionality."""

    def test_mutation_ledger_imports(self):
        """Test mutation_ledger module imports."""
        from agentic_core import mutation_ledger
        assert mutation_ledger is not None

    def test_mutation_ledger_class(self):
        """Test MutationLedger class exists."""
        from agentic_core import MutationLedger
        assert MutationLedger is not None

    def test_mutation_ledger_callable(self):
        """Test mutation_ledger functions are callable."""
        from agentic_core import validate_mutation_ledger
        assert callable(validate_mutation_ledger)

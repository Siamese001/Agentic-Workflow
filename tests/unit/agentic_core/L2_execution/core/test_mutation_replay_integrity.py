"""Test MutationReplayIntegrity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMutationReplayIntegrity:
    """Test MutationReplayIntegrity functionality."""

    def test_mutation_replay_integrity_imports(self):
        """Test mutation_replay_integrity module imports."""
        from agentic_core import mutation_replay_integrity

        assert mutation_replay_integrity is not None

    def test_mutation_replay_integrity_class(self):
        """Test MutationReplayIntegrity class exists."""
        from agentic_core import MutationReplayIntegrity

        assert MutationReplayIntegrity is not None

    def test_mutation_replay_integrity_callable(self):
        """Test mutation_replay_integrity functions are callable."""
        from agentic_core import validate_mutation_replay_integrity

        assert callable(validate_mutation_replay_integrity)

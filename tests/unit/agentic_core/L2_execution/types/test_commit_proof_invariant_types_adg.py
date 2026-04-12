"""Test CommitProofInvariantTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCommitProofInvariantTypesAdg:
    """Test CommitProofInvariantTypesAdg functionality."""

    def test_commit_proof_invariant_types_adg_imports(self):
        """Test commit_proof_invariant_types_adg module imports."""
        from agentic_core import commit_proof_invariant_types_adg

        assert commit_proof_invariant_types_adg is not None

    def test_commit_proof_invariant_types_adg_class(self):
        """Test CommitProofInvariantTypesAdg class exists."""
        from agentic_core import CommitProofInvariantTypesAdg

        assert CommitProofInvariantTypesAdg is not None

    def test_commit_proof_invariant_types_adg_callable(self):
        """Test commit_proof_invariant_types_adg functions are callable."""
        from agentic_core import validate_commit_proof_invariant_types_adg

        assert callable(validate_commit_proof_invariant_types_adg)

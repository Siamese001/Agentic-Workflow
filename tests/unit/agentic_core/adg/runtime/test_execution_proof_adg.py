"""Test ExecutionProofAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionProofAdg:
    """Test ExecutionProofAdg functionality."""

    def test_execution_proof_adg_imports(self):
        """Test execution_proof_adg module imports."""
        from agentic_core import execution_proof_adg
        assert execution_proof_adg is not None

    def test_execution_proof_adg_class(self):
        """Test ExecutionProofAdg class exists."""
        from agentic_core import ExecutionProofAdg
        assert ExecutionProofAdg is not None

    def test_execution_proof_adg_callable(self):
        """Test execution_proof_adg functions are callable."""
        from agentic_core import validate_execution_proof_adg
        assert callable(validate_execution_proof_adg)

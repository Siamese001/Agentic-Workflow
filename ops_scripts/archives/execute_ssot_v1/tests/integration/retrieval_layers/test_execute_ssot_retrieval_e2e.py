"""Test ExecuteSsotRetrievalE2e functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecuteSsotRetrievalE2e:
    """Test ExecuteSsotRetrievalE2e functionality."""

    def test_execute_ssot_retrieval_e2e_imports(self):
        """Test execute_ssot_retrieval_e2e module imports."""
        from agentic_core import execute_ssot_retrieval_e2e
        assert execute_ssot_retrieval_e2e is not None

    def test_execute_ssot_retrieval_e2e_class(self):
        """Test ExecuteSsotRetrievalE2e class exists."""
        from agentic_core import ExecuteSsotRetrievalE2e
        assert ExecuteSsotRetrievalE2e is not None

    def test_execute_ssot_retrieval_e2e_callable(self):
        """Test execute_ssot_retrieval_e2e functions are callable."""
        from agentic_core import validate_execute_ssot_retrieval_e2e
        assert callable(validate_execute_ssot_retrieval_e2e)

"""Test RagImportContract functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRagImportContract:
    """Test RagImportContract functionality."""

    def test_rag_import_contract_imports(self):
        """Test rag_import_contract module imports."""
        from agentic_core import rag_import_contract

        assert rag_import_contract is not None

    def test_rag_import_contract_class(self):
        """Test RagImportContract class exists."""
        from agentic_core import RagImportContract

        assert RagImportContract is not None

    def test_rag_import_contract_callable(self):
        """Test rag_import_contract functions are callable."""
        from agentic_core import validate_rag_import_contract

        assert callable(validate_rag_import_contract)

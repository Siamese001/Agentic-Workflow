"""Test MetaLearningContract functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningContract:
    """Test MetaLearningContract functionality."""

    def test_meta_learning_contract_imports(self):
        """Test meta_learning_contract module imports."""
        from agentic_core import meta_learning_contract
        assert meta_learning_contract is not None

    def test_meta_learning_contract_class(self):
        """Test MetaLearningContract class exists."""
        from agentic_core import MetaLearningContract
        assert MetaLearningContract is not None

    def test_meta_learning_contract_callable(self):
        """Test meta_learning_contract functions are callable."""
        from agentic_core import validate_meta_learning_contract
        assert callable(validate_meta_learning_contract)

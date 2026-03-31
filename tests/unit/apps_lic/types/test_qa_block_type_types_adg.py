"""Test QaBlockTypeTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQaBlockTypeTypesAdg:
    """Test QaBlockTypeTypesAdg functionality."""

    def test_qa_block_type_types_adg_imports(self):
        """Test qa_block_type_types_adg module imports."""
        from agentic_core import qa_block_type_types_adg
        assert qa_block_type_types_adg is not None

    def test_qa_block_type_types_adg_class(self):
        """Test QaBlockTypeTypesAdg class exists."""
        from agentic_core import QaBlockTypeTypesAdg
        assert QaBlockTypeTypesAdg is not None

    def test_qa_block_type_types_adg_callable(self):
        """Test qa_block_type_types_adg functions are callable."""
        from agentic_core import validate_qa_block_type_types_adg
        assert callable(validate_qa_block_type_types_adg)

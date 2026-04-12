"""Test TokenizationAdapterAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTokenizationAdapterAdg:
    """Test TokenizationAdapterAdg functionality."""

    def test_tokenization_adapter_adg_imports(self):
        """Test tokenization_adapter_adg module imports."""
        from agentic_core import tokenization_adapter_adg

        assert tokenization_adapter_adg is not None

    def test_tokenization_adapter_adg_class(self):
        """Test TokenizationAdapterAdg class exists."""
        from agentic_core import TokenizationAdapterAdg

        assert TokenizationAdapterAdg is not None

    def test_tokenization_adapter_adg_callable(self):
        """Test tokenization_adapter_adg functions are callable."""
        from agentic_core import validate_tokenization_adapter_adg

        assert callable(validate_tokenization_adapter_adg)

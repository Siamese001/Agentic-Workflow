"""Test ImemorystoreprotocolAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestImemorystoreprotocolAdg:
    """Test ImemorystoreprotocolAdg functionality."""

    def test_IMemoryStoreProtocol_adg_imports(self):
        """Test IMemoryStoreProtocol_adg module imports."""
        from agentic_core import IMemoryStoreProtocol_adg
        assert IMemoryStoreProtocol_adg is not None

    def test_IMemoryStoreProtocol_adg_class(self):
        """Test ImemorystoreprotocolAdg class exists."""
        from agentic_core import ImemorystoreprotocolAdg
        assert ImemorystoreprotocolAdg is not None

    def test_IMemoryStoreProtocol_adg_callable(self):
        """Test IMemoryStoreProtocol_adg functions are callable."""
        from agentic_core import validate_IMemoryStoreProtocol_adg
        assert callable(validate_IMemoryStoreProtocol_adg)

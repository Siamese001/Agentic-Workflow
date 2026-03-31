"""Test SovereigntyRuntimeContract functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereigntyRuntimeContract:
    """Test SovereigntyRuntimeContract functionality."""

    def test_sovereignty_runtime_contract_imports(self):
        """Test sovereignty_runtime_contract module imports."""
        from agentic_core import sovereignty_runtime_contract
        assert sovereignty_runtime_contract is not None

    def test_sovereignty_runtime_contract_class(self):
        """Test SovereigntyRuntimeContract class exists."""
        from agentic_core import SovereigntyRuntimeContract
        assert SovereigntyRuntimeContract is not None

    def test_sovereignty_runtime_contract_callable(self):
        """Test sovereignty_runtime_contract functions are callable."""
        from agentic_core import validate_sovereignty_runtime_contract
        assert callable(validate_sovereignty_runtime_contract)

"""Test ToolContractValidation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolContractValidation:
    """Test ToolContractValidation functionality."""

    def test_tool_contract_validation_imports(self):
        """Test tool_contract_validation module imports."""
        from agentic_core import tool_contract_validation
        assert tool_contract_validation is not None

    def test_tool_contract_validation_class(self):
        """Test ToolContractValidation class exists."""
        from agentic_core import ToolContractValidation
        assert ToolContractValidation is not None

    def test_tool_contract_validation_callable(self):
        """Test tool_contract_validation functions are callable."""
        from agentic_core import validate_tool_contract_validation
        assert callable(validate_tool_contract_validation)

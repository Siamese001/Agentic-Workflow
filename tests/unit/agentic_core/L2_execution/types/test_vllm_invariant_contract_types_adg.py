"""Test VllmInvariantContractTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmInvariantContractTypesAdg:
    """Test VllmInvariantContractTypesAdg functionality."""

    def test_vllm_invariant_contract_types_adg_imports(self):
        """Test vllm_invariant_contract_types_adg module imports."""
        from agentic_core import vllm_invariant_contract_types_adg

        assert vllm_invariant_contract_types_adg is not None

    def test_vllm_invariant_contract_types_adg_class(self):
        """Test VllmInvariantContractTypesAdg class exists."""
        from agentic_core import VllmInvariantContractTypesAdg

        assert VllmInvariantContractTypesAdg is not None

    def test_vllm_invariant_contract_types_adg_callable(self):
        """Test vllm_invariant_contract_types_adg functions are callable."""
        from agentic_core import validate_vllm_invariant_contract_types_adg

        assert callable(validate_vllm_invariant_contract_types_adg)

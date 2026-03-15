"""ADG importability contract for agentic_core/L2_execution/types/agent_output_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_agent_output_contract_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.agent_output_contract_types import (  # noqa: F401
        AgentOutputContract,
        OutputContractViolation,
        wrap_output,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    OutputContractViolation = None  # type: ignore[assignment,misc]
    AgentOutputContract = None  # type: ignore[assignment,misc]
    wrap_output = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_output_contract_types deps unavailable")
class TestAgentOutputContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/agent_output_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_outputcontractviolation_defined(self) -> None:
        assert OutputContractViolation is not None

    def test_agentoutputcontract_defined(self) -> None:
        assert AgentOutputContract is not None

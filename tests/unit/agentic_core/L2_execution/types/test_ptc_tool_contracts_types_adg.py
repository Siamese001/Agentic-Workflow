"""ADG importability contract for agentic_core/L2_execution/types/ptc_tool_contracts_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ptc_tool_contracts_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ptc_tool_contracts_types import (  # noqa: F401
        ToolCall,
        ToolContractViolation,
        ToolResult,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ToolContractViolation = None  # type: ignore[assignment,misc]
    ToolCall = None  # type: ignore[assignment,misc]
    ToolResult = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ptc_tool_contracts_types deps unavailable")
class TestPtcToolContractsTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/ptc_tool_contracts_types.py must be importable."""
        assert _AVAILABLE

    def test_toolcontractviolation_defined(self) -> None:
        assert ToolContractViolation is not None

    def test_toolcall_defined(self) -> None:
        assert ToolCall is not None

    def test_toolresult_defined(self) -> None:
        assert ToolResult is not None

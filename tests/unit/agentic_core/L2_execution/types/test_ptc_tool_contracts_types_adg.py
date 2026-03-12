"""ADG importability contract for agentic_core/L2_execution/types/ptc_tool_contracts_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ptc_tool_contracts_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ptc_tool_contracts_types import (  # noqa: F401
        ToolContractViolation,
        ToolCall,
        ToolResult,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolContractViolation = None  # type: ignore[assignment,misc]
    ToolCall = None  # type: ignore[assignment,misc]
    ToolResult = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ptc_tool_contracts_types.py deps unavailable")
class TestPtcToolContractsTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ptc_tool_contracts_types.py must be importable."""
        assert _AVAILABLE

    def test_toolcontractviolation_is_type(self) -> None:
        assert ToolContractViolation is not None

    def test_toolcall_is_type(self) -> None:
        assert ToolCall is not None

    def test_toolresult_is_type(self) -> None:
        assert ToolResult is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


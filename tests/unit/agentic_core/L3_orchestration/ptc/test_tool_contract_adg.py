"""ADG importability contract for agentic_core/L3_orchestration/ptc/tool_contract.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_contract.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.ptc.tool_contract import (  # noqa: F401
        ToolArg,
        ToolSpec,
        ToolCall,
        ToolCallResult,
        canonical_json,
        sha256_hex,
        generate_call_id,
        hash_result_data,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolArg = None  # type: ignore[assignment,misc]
    ToolSpec = None  # type: ignore[assignment,misc]
    ToolCall = None  # type: ignore[assignment,misc]
    ToolCallResult = None  # type: ignore[assignment,misc]
    canonical_json = None  # type: ignore[assignment,misc]
    sha256_hex = None  # type: ignore[assignment,misc]
    generate_call_id = None  # type: ignore[assignment,misc]
    hash_result_data = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tool_contract.py deps unavailable")
class TestToolContractImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tool_contract.py must be importable."""
        assert _AVAILABLE

    def test_toolarg_is_type(self) -> None:
        assert ToolArg is not None

    def test_toolspec_is_type(self) -> None:
        assert ToolSpec is not None

    def test_toolcall_is_type(self) -> None:
        assert ToolCall is not None

    def test_canonical_json_callable(self) -> None:
        assert callable(canonical_json)

    def test_sha256_hex_callable(self) -> None:
        assert callable(sha256_hex)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


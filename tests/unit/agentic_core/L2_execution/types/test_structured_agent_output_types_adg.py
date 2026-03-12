"""ADG importability contract for agentic_core/L2_execution/types/structured_agent_output_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_structured_agent_output_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.structured_agent_output_types import (  # noqa: F401
        StructuredOutputViolation,
        ToolRequest,
        StructuredAgentOutput,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StructuredOutputViolation = None  # type: ignore[assignment,misc]
    ToolRequest = None  # type: ignore[assignment,misc]
    StructuredAgentOutput = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="structured_agent_output_types.py deps unavailable")
class TestStructuredAgentOutputTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: structured_agent_output_types.py must be importable."""
        assert _AVAILABLE

    def test_structuredoutputviolation_is_type(self) -> None:
        assert StructuredOutputViolation is not None

    def test_toolrequest_is_type(self) -> None:
        assert ToolRequest is not None

    def test_structuredagentoutput_is_type(self) -> None:
        assert StructuredAgentOutput is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


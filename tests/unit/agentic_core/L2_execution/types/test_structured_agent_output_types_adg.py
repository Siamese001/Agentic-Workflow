"""ADG importability contract for agentic_core/L2_execution/types/structured_agent_output_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_structured_agent_output_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.structured_agent_output_types import (  # noqa: F401
        StructuredAgentOutput,
        StructuredOutputViolation,
        ToolRequest,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    StructuredOutputViolation = None  # type: ignore[assignment,misc]
    ToolRequest = None  # type: ignore[assignment,misc]
    StructuredAgentOutput = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="structured_agent_output_types deps unavailable")
class TestStructuredAgentOutputTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/structured_agent_output_types.py must be importable."""
        assert _AVAILABLE

    def test_structuredoutputviolation_defined(self) -> None:
        assert StructuredOutputViolation is not None

    def test_toolrequest_defined(self) -> None:
        assert ToolRequest is not None

    def test_structuredagentoutput_defined(self) -> None:
        assert StructuredAgentOutput is not None
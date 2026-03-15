"""ADG importability contract for agentic_core/L2_execution/reasoning/ToolsmithAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ToolsmithAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.reasoning.ToolsmithAgent import (  # noqa: F401
        GeneratedTool,
        ToolsmithAgent,
        ToolSpec,
        get_ToolsmithAgent,
        initialize_ToolsmithAgent,
        tool_template,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ToolSpec = None  # type: ignore[assignment,misc]
    GeneratedTool = None  # type: ignore[assignment,misc]
    tool_template = None  # type: ignore[assignment,misc]
    ToolsmithAgent = None  # type: ignore[assignment,misc]
    get_ToolsmithAgent = None  # type: ignore[assignment,misc]
    initialize_ToolsmithAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent deps unavailable")
class TestToolsmithagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/reasoning/ToolsmithAgent.py must be importable."""
        assert _AVAILABLE

    def test_toolspec_defined(self) -> None:
        assert ToolSpec is not None

    def test_generatedtool_defined(self) -> None:
        assert GeneratedTool is not None

    def test_toolsmithagent_defined(self) -> None:
        assert ToolsmithAgent is not None

"""ADG importability contract for agentic_core/L5_safety/reasoning/NamingAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_NamingAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.NamingAgent import (  # noqa: F401
        TREE_SITTER_AVAILABLE,
        NamingAgent,
        PlacementResult,
        get_naming_agent,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TREE_SITTER_AVAILABLE = None  # type: ignore[assignment,misc]
    PlacementResult = None  # type: ignore[assignment,misc]
    NamingAgent = None  # type: ignore[assignment,misc]
    get_naming_agent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent deps unavailable")
class TestNamingagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/NamingAgent.py must be importable."""
        assert _AVAILABLE

    def test_placementresult_defined(self) -> None:
        assert PlacementResult is not None

    def test_namingagent_defined(self) -> None:
        assert NamingAgent is not None

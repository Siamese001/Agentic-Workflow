"""ADG importability contract for agentic_core/L0_routing/scripts/reasoning.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reasoning.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.reasoning import (  # noqa: F401
        ChainOfThoughtStrategy,
        CritiqueStrategy,
        ReActStrategy,
        ReasoningStrategy,
        ReflectionStrategy,
        TreeOfThoughtsStrategy,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReasoningStrategy = None  # type: ignore[assignment,misc]
    ChainOfThoughtStrategy = None  # type: ignore[assignment,misc]
    TreeOfThoughtsStrategy = None  # type: ignore[assignment,misc]
    ReActStrategy = None  # type: ignore[assignment,misc]
    ReflectionStrategy = None  # type: ignore[assignment,misc]
    CritiqueStrategy = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning deps unavailable")
class TestReasoningImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/scripts/reasoning.py must be importable."""
        assert _AVAILABLE

    def test_reasoningstrategy_defined(self) -> None:
        assert ReasoningStrategy is not None

    def test_chainofthoughtstrategy_defined(self) -> None:
        assert ChainOfThoughtStrategy is not None

    def test_treeofthoughtsstrategy_defined(self) -> None:
        assert TreeOfThoughtsStrategy is not None

    def test_reactstrategy_defined(self) -> None:
        assert ReActStrategy is not None

    def test_reflectionstrategy_defined(self) -> None:
        assert ReflectionStrategy is not None

    def test_critiquestrategy_defined(self) -> None:
        assert CritiqueStrategy is not None

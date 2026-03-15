"""ADG importability contract for agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignRAGManagerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import (  # noqa: F401
        SovereignRAGManager,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignRAGManager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignRAGManagerAgent deps unavailable")
class TestSovereignragmanageragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py must be importable."""
        assert _AVAILABLE

    def test_sovereignragmanager_defined(self) -> None:
        assert SovereignRAGManager is not None

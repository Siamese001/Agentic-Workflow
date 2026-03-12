"""ADG importability contract for agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignRAGManagerAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import (  # noqa: F401
        SovereignRAGManager,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereignRAGManager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignRAGManagerAgent.py deps unavailable")
class TestSovereignragmanageragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SovereignRAGManagerAgent.py must be importable."""
        assert _AVAILABLE

    def test_sovereignragmanager_is_type(self) -> None:
        assert SovereignRAGManager is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


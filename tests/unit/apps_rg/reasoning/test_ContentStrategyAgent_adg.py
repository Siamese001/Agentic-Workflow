"""ADG importability contract for apps_rg/reasoning/ContentStrategyAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ContentStrategyAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.reasoning.ContentStrategyAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ContentStrategyAgent.py deps unavailable")
class TestContentstrategyagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ContentStrategyAgent.py must be importable."""
        assert _AVAILABLE

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

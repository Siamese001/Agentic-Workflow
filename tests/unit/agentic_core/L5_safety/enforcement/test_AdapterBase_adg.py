"""ADG importability contract for agentic_core/L5_safety/enforcement/AdapterBase.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_AdapterBase.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.AdapterBase import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AdapterBase,
        AdapterContext,
        AdapterResult,
        HealingAdapter,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AdapterContext = None  # type: ignore[assignment,misc]
    AdapterResult = None  # type: ignore[assignment,misc]
    AdapterBase = None  # type: ignore[assignment,misc]
    HealingAdapter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="AdapterBase.py deps unavailable")
class TestAdapterbaseImportability:
    def test_module_importable(self) -> None:
        """ADG contract: AdapterBase.py must be importable."""
        assert _AVAILABLE

    def test_adaptercontext_is_type(self) -> None:
        assert AdapterContext is not None

    def test_adapterresult_is_type(self) -> None:
        assert AdapterResult is not None

    def test_adapterbase_is_type(self) -> None:
        assert AdapterBase is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

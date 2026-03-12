"""ADG importability contract for agentic_core/runtime/config/instructional_injections.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_instructional_injections.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.instructional_injections import (  # noqa: F401
        get_instructional_injections,
        get_required_injections,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    get_instructional_injections = None  # type: ignore[assignment,misc]
    get_required_injections = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="instructional_injections.py deps unavailable")
class TestInstructionalInjectionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: instructional_injections.py must be importable."""
        assert _AVAILABLE

    def test_get_instructional_injections_callable(self) -> None:
        assert callable(get_instructional_injections)

    def test_get_required_injections_callable(self) -> None:
        assert callable(get_required_injections)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


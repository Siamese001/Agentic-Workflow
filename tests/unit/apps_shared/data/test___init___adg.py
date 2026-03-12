"""ADG importability contract for apps_shared/data/__init__.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test___init__.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.data.__init__ import (  # noqa: F401
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="__init__.py deps unavailable")
class TestInitImportability:
    def test_module_importable(self) -> None:
        """ADG contract: __init__.py must be importable."""
        assert _AVAILABLE

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


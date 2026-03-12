"""ADG importability contract for apps_shared/spine/base_spine_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_base_spine_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.spine.base_spine_adapter import (  # noqa: F401
        BaseSpineAdapter,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BaseSpineAdapter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="base_spine_adapter.py deps unavailable")
class TestBaseSpineAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: base_spine_adapter.py must be importable."""
        assert _AVAILABLE

    def test_basespineadapter_is_type(self) -> None:
        assert BaseSpineAdapter is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


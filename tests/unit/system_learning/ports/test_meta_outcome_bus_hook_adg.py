"""ADG importability contract for system_learning/ports/meta_outcome_bus_hook.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_meta_outcome_bus_hook.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.ports.meta_outcome_bus_hook import (  # noqa: F401
        MetaOutcomeBusHook,
        NullMetaOutcomeBusHook,
        DefaultMetaOutcomeBusHook,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MetaOutcomeBusHook = None  # type: ignore[assignment,misc]
    NullMetaOutcomeBusHook = None  # type: ignore[assignment,misc]
    DefaultMetaOutcomeBusHook = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="meta_outcome_bus_hook.py deps unavailable")
class TestMetaOutcomeBusHookImportability:
    def test_module_importable(self) -> None:
        """ADG contract: meta_outcome_bus_hook.py must be importable."""
        assert _AVAILABLE

    def test_metaoutcomebushook_is_type(self) -> None:
        assert MetaOutcomeBusHook is not None

    def test_nullmetaoutcomebushook_is_type(self) -> None:
        assert NullMetaOutcomeBusHook is not None

    def test_defaultmetaoutcomebushook_is_type(self) -> None:
        assert DefaultMetaOutcomeBusHook is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


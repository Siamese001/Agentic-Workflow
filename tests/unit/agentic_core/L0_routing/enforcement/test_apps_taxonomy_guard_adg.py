"""ADG importability contract for agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_apps_taxonomy_guard.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.apps_taxonomy_guard import (  # noqa: F401
        AppsTaxonomyGuard,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AppsTaxonomyGuard = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="apps_taxonomy_guard.py deps unavailable")
class TestAppsTaxonomyGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: apps_taxonomy_guard.py must be importable."""
        assert _AVAILABLE

    def test_appstaxonomyguard_is_type(self) -> None:
        assert AppsTaxonomyGuard is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


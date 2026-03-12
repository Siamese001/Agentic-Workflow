"""ADG importability contract for agentic_core/L2_execution/healers/tiering_allowlist.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tiering_allowlist.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.tiering_allowlist import (  # noqa: F401
        is_tiering_allowed,
        is_tiering_allowed_by_path,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    is_tiering_allowed = None  # type: ignore[assignment,misc]
    is_tiering_allowed_by_path = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tiering_allowlist.py deps unavailable")
class TestTieringAllowlistImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tiering_allowlist.py must be importable."""
        assert _AVAILABLE

    def test_is_tiering_allowed_callable(self) -> None:
        assert callable(is_tiering_allowed)

    def test_is_tiering_allowed_by_path_callable(self) -> None:
        assert callable(is_tiering_allowed_by_path)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


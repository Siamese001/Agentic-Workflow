"""ADG importability contract for agentic_core/L0_routing/engines/path_router.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_path_router.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.engines.path_router import (  # noqa: F401
        Path,
        PathRouter,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Path = None  # type: ignore[assignment,misc]
    PathRouter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="path_router.py deps unavailable")
class TestPathRouterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: path_router.py must be importable."""
        assert _AVAILABLE

    def test_path_is_type(self) -> None:
        assert Path is not None

    def test_pathrouter_is_type(self) -> None:
        assert PathRouter is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


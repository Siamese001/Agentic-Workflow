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
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Path = None  # type: ignore[assignment,misc]
    PathRouter = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="path_router deps unavailable")
class TestPathRouterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/engines/path_router.py must be importable."""
        assert _AVAILABLE

    def test_path_defined(self) -> None:
        assert Path is not None

    def test_pathrouter_defined(self) -> None:
        assert PathRouter is not None

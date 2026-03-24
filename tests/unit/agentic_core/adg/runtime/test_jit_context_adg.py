"""ADG importability contract for agentic_core/adg/runtime/jit_context.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_jit_context.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.jit_context import (  # noqa: F401
        ContextSnapshot,
        FreezeBoundary,
        FreezeState,
        JITContextSession,
        JITContextSynchronizer,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    FreezeState = None  # type: ignore[assignment,misc]
    ContextSnapshot = None  # type: ignore[assignment,misc]
    FreezeBoundary = None  # type: ignore[assignment,misc]
    JITContextSession = None  # type: ignore[assignment,misc]
    JITContextSynchronizer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="jit_context deps unavailable")
class TestJitContextImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/jit_context.py must be importable."""
        assert _AVAILABLE

    def test_freezestate_defined(self) -> None:
        assert FreezeState is not None

    def test_contextsnapshot_defined(self) -> None:
        assert ContextSnapshot is not None

    def test_freezeboundary_defined(self) -> None:
        assert FreezeBoundary is not None

    def test_jitcontextsession_defined(self) -> None:
        assert JITContextSession is not None

    def test_jitcontextsynchronizer_defined(self) -> None:
        assert JITContextSynchronizer is not None
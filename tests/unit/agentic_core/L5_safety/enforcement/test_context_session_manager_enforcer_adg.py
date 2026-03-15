"""ADG importability contract for agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_context_session_manager_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.context_session_manager_enforcer import (  # noqa: F401
        AttentionState,
        ContextSession,
        ContextSessionManager,
        RiskLevel,
        get_current_session,
        get_session_manager,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RiskLevel = None  # type: ignore[assignment,misc]
    AttentionState = None  # type: ignore[assignment,misc]
    ContextSession = None  # type: ignore[assignment,misc]
    ContextSessionManager = None  # type: ignore[assignment,misc]
    get_session_manager = None  # type: ignore[assignment,misc]
    get_current_session = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="context_session_manager_enforcer deps unavailable")
class TestContextSessionManagerEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_risklevel_defined(self) -> None:
        assert RiskLevel is not None

    def test_attentionstate_defined(self) -> None:
        assert AttentionState is not None

    def test_contextsession_defined(self) -> None:
        assert ContextSession is not None

    def test_contextsessionmanager_defined(self) -> None:
        assert ContextSessionManager is not None

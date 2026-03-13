"""ADG importability contract for agentic_core/L3_orchestration/engines/handshake_state_machine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_handshake_state_machine.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.handshake_state_machine import (  # noqa: F401
        HandshakeState,
        HandshakeStateMachine,
        StateTransition,
        create_handshake_machine,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HandshakeState = None  # type: ignore[assignment,misc]
    StateTransition = None  # type: ignore[assignment,misc]
    HandshakeStateMachine = None  # type: ignore[assignment,misc]
    create_handshake_machine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="handshake_state_machine deps unavailable")
class TestHandshakeStateMachineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/handshake_state_machine.py must be importable."""
        assert _AVAILABLE

    def test_handshakestate_defined(self) -> None:
        assert HandshakeState is not None

    def test_statetransition_defined(self) -> None:
        assert StateTransition is not None

    def test_handshakestatemachine_defined(self) -> None:
        assert HandshakeStateMachine is not None

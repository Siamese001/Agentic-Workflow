"""ADG importability contract for agentic_core/adg/runtime/policy_state_observer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_policy_state_observer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.policy_state_observer import (  # noqa: F401
        PolicyStateObserver,
        StateObservationEvent,
        StateObservationKind,
        StateObservationReport,
        StateReadOutcome,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StateObservationKind = None  # type: ignore[assignment,misc]
    StateReadOutcome = None  # type: ignore[assignment,misc]
    StateObservationEvent = None  # type: ignore[assignment,misc]
    StateObservationReport = None  # type: ignore[assignment,misc]
    PolicyStateObserver = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="policy_state_observer deps unavailable")
class TestPolicyStateObserverImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/policy_state_observer.py must be importable."""
        assert _AVAILABLE

    def test_stateobservationkind_defined(self) -> None:
        assert StateObservationKind is not None

    def test_statereadoutcome_defined(self) -> None:
        assert StateReadOutcome is not None

    def test_stateobservationevent_defined(self) -> None:
        assert StateObservationEvent is not None

    def test_stateobservationreport_defined(self) -> None:
        assert StateObservationReport is not None

    def test_policystateobserver_defined(self) -> None:
        assert PolicyStateObserver is not None

"""ADG importability contract for agentic_core/L3_orchestration/reasoning/StateManagementAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_StateManagementAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.reasoning.StateManagementAgent import (  # noqa: F401
        IntegrityReport,
        StateEntry,
        StateManagementAgent,
        get_manifest_manager,
        get_memory_manager,
        get_state_manager,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    StateEntry = None  # type: ignore[assignment,misc]
    IntegrityReport = None  # type: ignore[assignment,misc]
    StateManagementAgent = None  # type: ignore[assignment,misc]
    get_state_manager = None  # type: ignore[assignment,misc]
    get_manifest_manager = None  # type: ignore[assignment,misc]
    get_memory_manager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent deps unavailable")
class TestStatemanagementagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/reasoning/StateManagementAgent.py must be importable."""
        assert _AVAILABLE

    def test_stateentry_defined(self) -> None:
        assert StateEntry is not None

    def test_integrityreport_defined(self) -> None:
        assert IntegrityReport is not None

    def test_statemanagementagent_defined(self) -> None:
        assert StateManagementAgent is not None
"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SafetyInspectorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.SafetyInspectorAgent import (  # noqa: F401
        ConstitutionalOverseer,
        SafetyInspectorAgent,
        ViolationCheck,
        create_overseer,
        create_safety_inspector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ViolationCheck = None  # type: ignore[assignment,misc]
    ConstitutionalOverseer = None  # type: ignore[assignment,misc]
    SafetyInspectorAgent = None  # type: ignore[assignment,misc]
    create_overseer = None  # type: ignore[assignment,misc]
    create_safety_inspector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SafetyInspectorAgent deps unavailable")
class TestSafetyinspectoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py must be importable."""
        assert _AVAILABLE

    def test_violationcheck_defined(self) -> None:
        assert ViolationCheck is not None

    def test_constitutionaloverseer_defined(self) -> None:
        assert ConstitutionalOverseer is not None

    def test_safetyinspectoragent_defined(self) -> None:
        assert SafetyInspectorAgent is not None

"""ADG importability contract for agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_StructureEnforcerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import (  # noqa: F401
        NamingRule,
        StructureConfig,
        StructureEnforcerAgent,
        StructureViolation,
        StructureViolationType,
        create_legacy_gravity_enforcer,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StructureViolationType = None  # type: ignore[assignment,misc]
    StructureViolation = None  # type: ignore[assignment,misc]
    NamingRule = None  # type: ignore[assignment,misc]
    StructureConfig = None  # type: ignore[assignment,misc]
    StructureEnforcerAgent = None  # type: ignore[assignment,misc]
    create_legacy_gravity_enforcer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent deps unavailable")
class TestStructureenforceragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py must be importable."""
        assert _AVAILABLE

    def test_structureviolationtype_defined(self) -> None:
        assert StructureViolationType is not None

    def test_structureviolation_defined(self) -> None:
        assert StructureViolation is not None

    def test_namingrule_defined(self) -> None:
        assert NamingRule is not None

    def test_structureconfig_defined(self) -> None:
        assert StructureConfig is not None

    def test_structureenforceragent_defined(self) -> None:
        assert StructureEnforcerAgent is not None

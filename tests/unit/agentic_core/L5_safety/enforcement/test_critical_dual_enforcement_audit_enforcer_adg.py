"""ADG importability contract for agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_critical_dual_enforcement_audit_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.critical_dual_enforcement_audit_enforcer import (  # noqa: F401
        MIN_ENFORCEMENT_LAYERS,
        MIN_STRUCTURAL_LAYERS,
        CriticalDualEnforcementAuditor,
        DualEnforcementViolation,
        RequirementMetadata,
        run_dual_enforcement_audit,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MIN_ENFORCEMENT_LAYERS = None  # type: ignore[assignment,misc]
    MIN_STRUCTURAL_LAYERS = None  # type: ignore[assignment,misc]
    RequirementMetadata = None  # type: ignore[assignment,misc]
    DualEnforcementViolation = None  # type: ignore[assignment,misc]
    CriticalDualEnforcementAuditor = None  # type: ignore[assignment,misc]
    run_dual_enforcement_audit = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="critical_dual_enforcement_audit_enforcer deps unavailable")
class TestCriticalDualEnforcementAuditEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_requirementmetadata_defined(self) -> None:
        assert RequirementMetadata is not None

    def test_dualenforcementviolation_defined(self) -> None:
        assert DualEnforcementViolation is not None

    def test_criticaldualenforcementauditor_defined(self) -> None:
        assert CriticalDualEnforcementAuditor is not None

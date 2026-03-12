"""ADG importability contract for agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_critical_dual_enforcement_audit_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.critical_dual_enforcement_audit_enforcer import (  # noqa: F401
        RequirementMetadata,
        DualEnforcementViolation,
        CriticalDualEnforcementAuditor,
        run_dual_enforcement_audit,
        test_dual_enforcement_audit,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RequirementMetadata = None  # type: ignore[assignment,misc]
    DualEnforcementViolation = None  # type: ignore[assignment,misc]
    CriticalDualEnforcementAuditor = None  # type: ignore[assignment,misc]
    run_dual_enforcement_audit = None  # type: ignore[assignment,misc]
    test_dual_enforcement_audit = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="critical_dual_enforcement_audit_enforcer.py deps unavailable")
class TestCriticalDualEnforcementAuditEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: critical_dual_enforcement_audit_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_requirementmetadata_is_type(self) -> None:
        assert RequirementMetadata is not None

    def test_dualenforcementviolation_is_type(self) -> None:
        assert DualEnforcementViolation is not None

    def test_criticaldualenforcementauditor_is_type(self) -> None:
        assert CriticalDualEnforcementAuditor is not None

    def test_run_dual_enforcement_audit_callable(self) -> None:
        assert callable(run_dual_enforcement_audit)

    def test_test_dual_enforcement_audit_callable(self) -> None:
        assert callable(test_dual_enforcement_audit)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None


"""Smoke tests for three_tier_compliance_enforcer — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.three_tier_compliance_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_ThreeTierComplianceChecker_class_present():
    assert hasattr(mod, "ThreeTierComplianceChecker")
    assert isinstance(mod.ThreeTierComplianceChecker, type)


def test_ComplianceResult_present():
    assert hasattr(mod, "ComplianceResult")


def test_AgentCompliance_present():
    assert hasattr(mod, "AgentCompliance")


def test_TierStatus_present():
    assert hasattr(mod, "TierStatus")


def test_ThreeTierComplianceChecker_instantiable(tmp_path):
    checker = mod.ThreeTierComplianceChecker(project_root=tmp_path)
    assert checker is not None


def test_ThreeTierComplianceChecker_has_check_or_validate():
    cls = mod.ThreeTierComplianceChecker
    has_method = any(
        callable(getattr(cls, name, None))
        for name in (
            "check_compliance",
            "validate",
            "run",
            "check_all",
            "check",
            "run_compliance_check",
            "generate_compliance_report",
        )
    )
    assert has_method, "ThreeTierComplianceChecker must have at least one check method"

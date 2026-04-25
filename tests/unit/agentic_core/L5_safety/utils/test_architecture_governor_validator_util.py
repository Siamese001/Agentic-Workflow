"""Smoke tests for architecture_governor_validator_util — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.architecture_governor_validator_util")


def test_module_imports_clean():
    assert mod is not None


def test_GovernanceValidationResult_class_present():
    assert hasattr(mod, "GovernanceValidationResult")
    assert isinstance(mod.GovernanceValidationResult, type)


def test_validate_architecture_governance_callable():
    assert callable(mod.validate_architecture_governance)


def test_scan_governance_callable():
    assert callable(mod.scan_governance)

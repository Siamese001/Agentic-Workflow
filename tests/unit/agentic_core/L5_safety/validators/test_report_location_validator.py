"""Smoke tests for report_location_validator — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.report_location_validator")


def test_module_imports_clean():
    assert mod is not None


def test_ReportLocationValidator_class_present():
    assert hasattr(mod, "ReportLocationValidator")
    assert isinstance(mod.ReportLocationValidator, type)


def test_ReportValidationResult_class_present():
    assert hasattr(mod, "ReportValidationResult")
    assert isinstance(mod.ReportValidationResult, type)


def test_ReportInventory_class_present():
    assert hasattr(mod, "ReportInventory")
    assert isinstance(mod.ReportInventory, type)

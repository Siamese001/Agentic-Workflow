"""Smoke tests for ssot_scanner_enforcer — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.ssot_scanner_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_SSOTScanner_class_present():
    assert hasattr(mod, "SSOTScanner")
    assert isinstance(mod.SSOTScanner, type)


def test_AgentMetadata_present():
    assert hasattr(mod, "AgentMetadata")


def test_SSOTScanner_instantiable(tmp_path):
    scanner = mod.SSOTScanner(project_root=tmp_path)
    assert scanner is not None


def test_SSOTScanner_has_scan_methods():
    cls = mod.SSOTScanner
    assert callable(getattr(cls, "scan_agents", None))
    assert callable(getattr(cls, "find_gravity_violations", None))
    assert callable(getattr(cls, "get_compliance_stats", None))

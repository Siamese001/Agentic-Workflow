"""Smoke tests for SSOTFolderCleanupAgent — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent")


def test_module_imports_clean():
    assert mod is not None


def test_SSOTFolderCleanupAgent_class_present():
    assert hasattr(mod, "SSOTFolderCleanupAgent")
    assert isinstance(mod.SSOTFolderCleanupAgent, type)


def test_SSOTFolderCleanupAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.SSOTFolderCleanupAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_CleanupStats_present():
    assert hasattr(mod, "CleanupStats")
    assert isinstance(mod.CleanupStats, type)

"""Smoke tests for ssot_folder_check_util — wave 29."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.ssot_folder_check_util")


def test_module_imports_clean():
    assert mod is not None


def test_FilesystemSSOTReconcilerAgent_class_present():
    assert hasattr(mod, "FilesystemSSOTReconcilerAgent")
    assert isinstance(mod.FilesystemSSOTReconcilerAgent, type)


def test_main_callable():
    assert callable(mod.main)

"""Behavioral contract tests for agentic_core.adg.applications.execute_ssot_integration."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.applications.execute_ssot_integration"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_prerunadgreport_is_instantiable(mod):
    """PreRunADGReport is accessible and is a type."""
    cls = getattr(mod, "PreRunADGReport", None)
    assert cls is not None, "PreRunADGReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PreRunADGReport must be a class"


def test_build_pre_run_report_is_callable(mod):
    """build_pre_run_report is accessible and callable."""
    func = getattr(mod, "build_pre_run_report", None)
    assert func is not None, "build_pre_run_report must be defined in {MODULE_PATH}"
    assert callable(func), "build_pre_run_report must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_pre_run_log_is_callable(mod):
    """emit_pre_run_log is accessible and callable."""
    func = getattr(mod, "emit_pre_run_log", None)
    assert func is not None, "emit_pre_run_log must be defined in {MODULE_PATH}"
    assert callable(func), "emit_pre_run_log must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


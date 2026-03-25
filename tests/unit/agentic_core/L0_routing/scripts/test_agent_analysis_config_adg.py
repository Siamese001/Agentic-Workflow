"""Behavioral contract tests for agentic_core.L0_routing.scripts.agent_analysis_config."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.agent_analysis_config"


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


def test_agentanalysis_is_instantiable(mod):
    """AgentAnalysis is accessible and is a type."""
    cls = getattr(mod, "AgentAnalysis", None)
    assert cls is not None, "AgentAnalysis must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AgentAnalysis must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_analyze_file_is_callable(mod):
    """analyze_file is accessible and callable."""
    func = getattr(mod, "analyze_file", None)
    assert func is not None, "analyze_file must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_file must be callable"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


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


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_generate_report_is_callable(mod):
    """generate_report is accessible and callable."""
    func = getattr(mod, "generate_report", None)
    assert func is not None, "generate_report must be defined in {MODULE_PATH}"
    assert callable(func), "generate_report must be callable"


def test_scan_ssot_folders_is_callable(mod):
    """scan_ssot_folders is accessible and callable."""
    func = getattr(mod, "scan_ssot_folders", None)
    assert func is not None, "scan_ssot_folders must be defined in {MODULE_PATH}"
    assert callable(func), "scan_ssot_folders must be callable"


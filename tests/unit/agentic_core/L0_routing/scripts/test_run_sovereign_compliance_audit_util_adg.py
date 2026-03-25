"""Behavioral contract tests for agentic_core.L0_routing.scripts.run_sovereign_compliance_audit_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.run_sovereign_compliance_audit_util"


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


def test_invoke_code_validator_is_callable(mod):
    """invoke_code_validator is accessible and callable."""
    func = getattr(mod, "invoke_code_validator", None)
    assert func is not None, "invoke_code_validator must be defined in {MODULE_PATH}"
    assert callable(func), "invoke_code_validator must be callable"


def test_load_structure_enforcer_agent_is_callable(mod):
    """load_structure_enforcer_agent is accessible and callable."""
    func = getattr(mod, "load_structure_enforcer_agent", None)
    assert func is not None, "load_structure_enforcer_agent must be defined in {MODULE_PATH}"
    assert callable(func), "load_structure_enforcer_agent must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"


def test_run_code_validator_is_callable(mod):
    """run_code_validator is accessible and callable."""
    func = getattr(mod, "run_code_validator", None)
    assert func is not None, "run_code_validator must be defined in {MODULE_PATH}"
    assert callable(func), "run_code_validator must be callable"


def test_run_structure_enforcer_is_callable(mod):
    """run_structure_enforcer is accessible and callable."""
    func = getattr(mod, "run_structure_enforcer", None)
    assert func is not None, "run_structure_enforcer must be defined in {MODULE_PATH}"
    assert callable(func), "run_structure_enforcer must be callable"


"""Surface coverage for `agentic_core.L5_safety.reasoning.StructuralValidatorAgent`.

Wave 2 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. Security-surface
L5 gatekeeper — validates gravity/naming/ASCII rules for structure enforcement.
"""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.StructuralValidatorAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_public_classes_present(mod):
    for name in [
        "StructuralValidatorAgent",
        "StructureConfig",
        "StructureViolation",
        "StructureViolationType",
    ]:
        assert hasattr(mod, name), f"{name} missing from {MODULE}"


def test_structure_config_is_dataclass(mod):
    assert is_dataclass(mod.StructureConfig)
    cfg = mod.StructureConfig()
    assert cfg.enable_gravity is True
    assert cfg.enable_naming is True
    assert cfg.agent_suffix == "Agent"


def test_structure_violation_is_dataclass(mod):
    assert is_dataclass(mod.StructureViolation)


def test_violation_type_constants(mod):
    vt = mod.StructureViolationType
    for name in ("GRAVITY", "HIERARCHY", "NAMING", "DOCUMENTATION", "ASCII"):
        assert isinstance(getattr(vt, name), str)


def test_class_exposes_layer_order_and_gravity_rules(mod):
    cls = mod.StructuralValidatorAgent
    assert hasattr(cls, "LAYER_ORDER")
    assert hasattr(cls, "GRAVITY_RULES")


def test_public_methods_callable(mod):
    cls = mod.StructuralValidatorAgent
    for name in ("validate_file", "validate_structure", "force_rename_class", "heal"):
        attr = getattr(cls, name, None)
        assert callable(attr), f"{name} must be callable"


def test_heal_repository_raises_not_implemented(mod):
    cfg = mod.StructureConfig()
    agent = mod.StructuralValidatorAgent(config=cfg)
    with pytest.raises(NotImplementedError):
        agent.heal_repository()


def test_validate_file_returns_list_on_missing(mod, tmp_path):
    agent = mod.StructuralValidatorAgent()
    missing = tmp_path / "does_not_exist.py"
    result = agent.validate_file(missing)
    assert result == []


def test_heal_with_unknown_type_returns_skipped(mod):
    agent = mod.StructuralValidatorAgent()
    result = agent.heal({"type": "unknown", "path": "/nowhere"})
    assert isinstance(result, dict)
    assert result.get("skipped", 0) == 1


def test_config_project_root_defaults_to_cwd(mod):
    agent = mod.StructuralValidatorAgent()
    assert isinstance(agent.project_root, Path)

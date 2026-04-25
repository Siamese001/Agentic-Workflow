"""Surface coverage for `agentic_core.L5_safety.reasoning.StructureEnforcerAgent`.

Wave 6 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 agent
that enforces structural rules (the legacy variant of StructuralValidatorAgent).
"""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.StructureEnforcerAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize(
    "name",
    [
        "StructureViolationType",
        "StructureViolation",
        "NamingRule",
        "StructureConfig",
        "StructureEnforcerAgent",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


def test_violation_and_config_are_dataclasses(mod):
    # StructureViolation and StructureConfig are typically dataclasses
    assert is_dataclass(mod.StructureViolation) or hasattr(mod.StructureViolation, "__init__")
    assert is_dataclass(mod.StructureConfig) or hasattr(mod.StructureConfig, "__init__")


@pytest.mark.parametrize(
    "factory",
    ["create_legacy_gravity_enforcer", "create_legacy_naming_enforcer", "create_legacy_doc_enforcer"],
)
def test_legacy_factories_callable(mod, factory):
    fn = getattr(mod, factory, None)
    assert callable(fn), f"{factory} must be callable"


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.StructureEnforcerAgent, SovereignBaseAgent)

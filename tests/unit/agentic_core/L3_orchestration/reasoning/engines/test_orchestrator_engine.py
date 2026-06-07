"""Surface coverage for `agentic_core.L3_orchestration.reasoning.engines.orchestrator_engine`.

Wave 8 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L3
orchestration core. Highest fan-out untested module (21).
"""

from __future__ import annotations

import inspect
from enum import Enum

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L3_orchestration.reasoning.engines.orchestrator_engine"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize(
    "name",
    [
        "L3OrchestrationStrategy",
        "OrchestratorMode",
        "Orchestrator",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


def test_orchestrator_mode_is_enum(mod):
    assert issubclass(mod.OrchestratorMode, Enum)
    assert len(list(mod.OrchestratorMode)) >= 1


def test_get_consolidated_orchestrator_callable(mod):
    assert hasattr(mod, "get_consolidated_orchestrator")
    assert callable(mod.get_consolidated_orchestrator)


def test_resolve_runtime_primitives_callable(mod):
    """Private helper must remain callable (gates lazy primitive imports)."""
    assert callable(mod._resolve_runtime_primitives)

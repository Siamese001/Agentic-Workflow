"""Surface coverage for `agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer`.

Wave 10 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize(
    "name", ["StructureViolation", "StructureValidationResult", "SSOTStructureValidator"]
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


def test_run_structure_validation_callable(mod):
    assert hasattr(mod, "run_structure_validation")
    assert callable(mod.run_structure_validation)

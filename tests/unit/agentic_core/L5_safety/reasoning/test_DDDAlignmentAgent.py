"""Surface coverage for `agentic_core.L5_safety.reasoning.DDDAlignmentAgent`.

Wave 7 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 agent
that validates Domain-Driven Design alignment.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.DDDAlignmentAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_classes_present(mod):
    assert hasattr(mod, "DDDAlignmentAgent")
    assert hasattr(mod, "DDDViolation")
    assert inspect.isclass(mod.DDDAlignmentAgent)
    assert inspect.isclass(mod.DDDViolation)


def test_validate_ddd_alignment_callable(mod):
    assert hasattr(mod, "validate_ddd_alignment")
    assert callable(mod.validate_ddd_alignment)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.DDDAlignmentAgent, SovereignBaseAgent)

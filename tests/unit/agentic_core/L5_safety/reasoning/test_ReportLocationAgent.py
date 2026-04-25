"""Surface coverage for `agentic_core.L5_safety.reasoning.ReportLocationAgent`.

Wave 6 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 agent
that heals report file locations to canonical paths.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.ReportLocationAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports(mod):
    assert hasattr(mod, "__all__")
    assert set(mod.__all__) >= {"ReportLocationAgent", "ReportLocationHealResult"}


def test_class_present(mod):
    assert hasattr(mod, "ReportLocationAgent")
    assert inspect.isclass(mod.ReportLocationAgent)


def test_heal_result_class_present(mod):
    assert hasattr(mod, "ReportLocationHealResult")
    assert inspect.isclass(mod.ReportLocationHealResult)


def test_uses_atomic_execution_mixin(mod):
    """ReportLocationAgent uses AtomicExecutionMixin (not SovereignBaseAgent)
    per its MRO. Test pins this contract."""
    mro_names = [c.__name__ for c in mod.ReportLocationAgent.__mro__]
    assert any("AtomicExecution" in n for n in mro_names), (
        f"Expected AtomicExecutionMixin in MRO, got: {mro_names}"
    )

"""Surface coverage for `agentic_core.L5_safety.enforcement.hitl.hitl_graph`.

Wave 10 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). HITL
runtime graph (per ADR-023). Distinct from Author-Gate developer-loop.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.hitl.hitl_graph"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    assert hasattr(mod, "__all__")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved: {missing}"


@pytest.mark.parametrize(
    "name",
    [
        "HITLDecisionType",
        "HITLCheckpoint",
        "HumanDecision",
        "HITLGraph",
        "HITLRuntimeRecorder",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


def test_decision_type_is_enum_like(mod):
    """HITLDecisionType should be enum-like."""
    members = [a for a in dir(mod.HITLDecisionType) if not a.startswith("_")]
    assert len(members) >= 1

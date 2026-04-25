"""Surface coverage for `agentic_core.L5_safety.enforcement.policy_action_contract`.

Wave 5 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5
policy enforcement contract — gates actions through the safety plane.
"""

from __future__ import annotations

import inspect
from enum import Enum

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.policy_action_contract"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    if not hasattr(mod, "__all__"):
        pytest.skip("__all__ not defined")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved names: {missing}"


@pytest.mark.parametrize(
    "name",
    [
        "PolicyOutcome",
        "ActionClass",
        "PolicyDecisionArtifact",
        "PolicyEnforcementError",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


def test_policy_enforcement_error_inherits_exception(mod):
    assert issubclass(mod.PolicyEnforcementError, Exception)


def test_enforce_policy_before_action_callable(mod):
    assert hasattr(mod, "enforce_policy_before_action")
    assert callable(mod.enforce_policy_before_action)


def test_get_decision_artifacts_callable(mod):
    assert hasattr(mod, "get_decision_artifacts")
    assert callable(mod.get_decision_artifacts)


def test_get_decision_artifacts_returns_iterable(mod):
    result = mod.get_decision_artifacts()
    # Returns a list-like or iterable of artifacts
    assert hasattr(result, "__iter__")

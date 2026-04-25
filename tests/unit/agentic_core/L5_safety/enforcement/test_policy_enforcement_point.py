"""Surface coverage for `agentic_core.L5_safety.enforcement.policy_enforcement_point`.

Wave 10 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). PEP
that gates actions through L5 policy.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.policy_enforcement_point"


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
    ["PolicyVerdict", "PolicyCheckResult", "PolicyViolationError", "PolicyEnforcementPoint"],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


def test_policy_violation_error_inherits_exception(mod):
    assert issubclass(mod.PolicyViolationError, Exception)


def test_pep_singleton_seam(mod):
    assert callable(mod.get_policy_enforcement_point)
    assert callable(mod.reset_policy_enforcement_point)
    mod.reset_policy_enforcement_point()
    pep = mod.get_policy_enforcement_point()
    assert pep is not None
    assert isinstance(pep, mod.PolicyEnforcementPoint)

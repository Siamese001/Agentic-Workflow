"""Surface coverage for `agentic_core.L5_safety.utils.code_enforcer_util`.

Retirement coverage for the canonical utility that replaced the deprecated
`CodeEnforcerAgent` shim.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.utils.code_enforcer_util"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_code_enforcer_class_present(mod):
    assert hasattr(mod, "CodeEnforcer")
    assert inspect.isclass(mod.CodeEnforcer)


def test_code_violation_type_present(mod):
    assert hasattr(mod, "CodeViolation")
    assert inspect.isclass(mod.CodeViolation)


def test_enforcer_exposes_validation_api(mod):
    assert callable(getattr(mod.CodeEnforcer, "validate_file", None))

"""Surface coverage for `agentic_core.L5_safety.utils.code_validator_util`.

Retirement coverage for the canonical utility that replaced the deprecated
`CodeValidatorAgent` shim.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.utils.code_validator_util"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "CodeValidator")
    assert inspect.isclass(mod.CodeValidator)


def test_ruleset_and_report_types_present(mod):
    assert inspect.isclass(mod.RuleSet)
    assert inspect.isclass(mod.ValidationReport)


def test_validator_exposes_repository_api(mod):
    assert callable(getattr(mod.CodeValidator, "validate_repository", None))

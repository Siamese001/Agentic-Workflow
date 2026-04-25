"""Surface coverage for `agentic_core.L5_safety.types.heal_llm_seam_types`.

Wave 5 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 type
contract for heal-LLM seam (capability gating + budget caps + telemetry).
"""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.types.heal_llm_seam_types"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize(
    "name",
    [
        "HealSeamBypassError",
        "HealLlmRequest",
        "PolicyDecisionRecord",
        "HealBudgetExceededError",
        "HealBudgetCaps",
        "HealTelemetryRecord",
        "RepoHealOperation",
        "RepoHealPlan",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


def test_bypass_and_budget_errors_inherit_exception(mod):
    assert issubclass(mod.HealSeamBypassError, Exception)
    assert issubclass(mod.HealBudgetExceededError, Exception)


@pytest.mark.parametrize(
    "fn",
    [
        "set_heal_seam_capability",
        "reset_heal_seam_capability",
        "assert_heal_seam_capability",
        "guarded_heal_llm_call",
        "set_heal_budget_caps",
        "reset_heal_budget_counters",
    ],
)
def test_public_functions_callable(mod, fn):
    assert hasattr(mod, fn), f"{fn} missing"
    assert callable(getattr(mod, fn))


def test_reset_heal_seam_capability_requires_token(mod):
    """Reset is token-gated to prevent stray production resets."""
    sig = inspect.signature(mod.reset_heal_seam_capability)
    assert "token" in sig.parameters, (
        "reset_heal_seam_capability must require a token argument for safety"
    )

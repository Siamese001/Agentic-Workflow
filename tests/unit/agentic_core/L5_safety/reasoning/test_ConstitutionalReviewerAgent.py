"""Surface coverage for `agentic_core.L5_safety.reasoning.ConstitutionalReviewerAgent`.

Wave 12 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). L5
agent that reviews compliance against constitutional rules.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.ConstitutionalReviewerAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize("name", ["ConstitutionalReviewResult", "ConstitutionalReviewerAgent"])
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


def test_track_metrics_callable(mod):
    assert hasattr(mod, "track_metrics")
    assert callable(mod.track_metrics)


def test_class_name_ends_with_agent(mod):
    assert mod.ConstitutionalReviewerAgent.__name__.endswith("Agent")

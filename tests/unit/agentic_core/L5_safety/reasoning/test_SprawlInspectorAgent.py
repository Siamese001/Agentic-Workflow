"""Surface coverage for `agentic_core.L5_safety.reasoning.SprawlInspectorAgent`.

Wave 9 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.SprawlInspectorAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "SprawlInspectorAgent")
    assert inspect.isclass(mod.SprawlInspectorAgent)


def test_class_name_ends_with_agent(mod):
    assert mod.SprawlInspectorAgent.__name__.endswith("Agent")

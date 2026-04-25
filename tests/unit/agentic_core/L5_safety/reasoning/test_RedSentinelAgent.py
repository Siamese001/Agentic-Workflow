"""Surface coverage for `agentic_core.L5_safety.reasoning.RedSentinelAgent`.

Wave 9 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.RedSentinelAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "RedSentinelAgent")
    assert inspect.isclass(mod.RedSentinelAgent)


def test_get_red_sentinel_callable(mod):
    assert hasattr(mod, "get_red_sentinel")
    assert callable(mod.get_red_sentinel)


def test_class_name_ends_with_agent(mod):
    assert mod.RedSentinelAgent.__name__.endswith("Agent")

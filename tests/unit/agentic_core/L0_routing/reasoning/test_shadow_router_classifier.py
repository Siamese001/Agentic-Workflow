"""Surface coverage for `agentic_core.L0_routing.reasoning.shadow_router_classifier`.

Wave 11 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.reasoning.shadow_router_classifier"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "ShadowRouterClassifier")
    assert inspect.isclass(mod.ShadowRouterClassifier)


def test_get_canonical_json_helper_callable(mod):
    assert callable(mod._get_canonical_json)

"""Surface coverage for `agentic_core.L0_routing.utils.root_customs_util`.

Wave 11 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.utils.root_customs_util"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize("name", ["RoutingDecision", "ASTAnalyzer"])
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


@pytest.mark.parametrize(
    "fn", ["scan_root_directory", "check_allowed_patterns", "analyze_content_signatures"]
)
def test_public_functions_callable(mod, fn):
    assert hasattr(mod, fn)
    assert callable(getattr(mod, fn))

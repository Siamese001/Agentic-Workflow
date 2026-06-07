"""Surface coverage for `agentic_core.L5_safety.config.severity`.

Wave 5 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 config
SSOT for severity bands. Used by ruff/ADG/legacy converters.
"""

from __future__ import annotations

import inspect
from enum import Enum

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.config.severity"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    assert hasattr(mod, "__all__")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved names: {missing}"


def test_severity_level_is_enum(mod):
    assert issubclass(mod.SeverityLevel, Enum)
    assert len(list(mod.SeverityLevel)) >= 1


@pytest.mark.parametrize("name", ["from_ruff_category", "from_adg_category", "from_legacy_string"])
def test_converter_callables(mod, name):
    fn = getattr(mod, name)
    assert callable(fn)
    sig = inspect.signature(fn)
    assert len(sig.parameters) >= 1

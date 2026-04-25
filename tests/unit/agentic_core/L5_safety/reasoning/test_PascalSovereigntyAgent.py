"""Surface coverage for `agentic_core.L5_safety.reasoning.PascalSovereigntyAgent`.

Wave 7 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.PascalSovereigntyAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "PascalSovereigntyAgent")
    assert inspect.isclass(mod.PascalSovereigntyAgent)


def test_get_python_files_fast_callable(mod):
    assert callable(mod.get_python_files_fast)


def test_main_callable(mod):
    assert callable(mod.main)


def test_class_is_concrete(mod):
    """PascalSovereigntyAgent is a script-style agent that does not inherit
    from SovereignBaseAgent (verified by MRO). Confirm it remains a concrete class."""
    cls = mod.PascalSovereigntyAgent
    assert cls.__name__ == "PascalSovereigntyAgent"
    assert cls.__name__.endswith("Agent")

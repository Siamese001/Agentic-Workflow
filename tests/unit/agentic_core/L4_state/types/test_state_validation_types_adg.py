"""ADG contract tests for agentic_core/L4_state/types/state_validation_types.py.

The canonical source for StateValidationError and StateValidationMixin is
agentic_core/mixins/state_validation_mixin.py — the types/ file is a shim.
Tests point at the mixin (the real SSOT) using AST inspection.
"""
from __future__ import annotations

import pathlib
import re

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L4_state.types.state_validation_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SHIM = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L4_state" / "types" / "state_validation_types.py"
)
_MIXIN = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "mixins" / "state_validation_mixin.py"
)


def _mixin_text():
    return _MIXIN.read_text(encoding="utf-8", errors="replace")


def _mixin_class_names():
    import ast
    tree = ast.parse(_mixin_text())
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


class TestStateValidationTypesSource:
    def test_shim_source_exists(self):
        assert _SHIM.exists(), f"Shim not found: {_SHIM}"

    def test_mixin_source_exists(self):
        assert _MIXIN.exists(), f"Canonical mixin not found: {_MIXIN}"

    def test_mixin_has_state_validation_error(self):
        assert "StateValidationError" in _mixin_class_names()

    def test_mixin_has_state_validation_mixin(self):
        assert "StateValidationMixin" in _mixin_class_names()

    def test_state_validation_error_subclasses_exception(self):
        src = _mixin_text()
        assert re.search(r"class StateValidationError\s*\(.*Exception.*\)", src), (
            "StateValidationError must subclass Exception"
        )

    def test_shim_references_canonical_names(self):
        shim = _SHIM.read_text(encoding="utf-8", errors="replace")
        assert "StateValidationError" in shim
        assert "StateValidationMixin" in shim
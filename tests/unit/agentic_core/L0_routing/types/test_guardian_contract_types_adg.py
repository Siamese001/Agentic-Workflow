"""ADG contract tests for agentic_core/L0_routing/types/guardian_contract_types.py
and v15_exceptions.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5] / "agentic_core" / "L0_routing" / "types" / "guardian_contract_types.py"
)
_SRC_V15 = pathlib.Path(__file__).parents[5] / "agentic_core" / "L0_routing" / "types" / "v15_exceptions.py"


def _tree(src=_SRC):
    return ast.parse(src.read_text(encoding="utf-8", errors="replace"))


def _class_names(src=_SRC):
    return {n.name for n in ast.walk(_tree(src)) if isinstance(n, ast.ClassDef)}


def _func_names(src=_SRC):
    return {n.name for n in ast.walk(_tree(src)) if isinstance(n, ast.FunctionDef)}


class TestGuardianContractTypesSource:
    """Generated test class for agentic_core.L0_routing.types.guardian_contract_types."""

    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_v15_enforcement_error(self):
        assert "V15EnforcementError" in _class_names(_SRC_V15)

    def test_has_v15_soft_fail_abort(self):
        assert "V15SoftFailAbort" in _class_names(_SRC_V15)

    def test_has_is_v15_enforced(self):
        assert "is_v15_enforced" in _func_names(_SRC_V15)

    def test_has_is_v15_hard_fail(self):
        assert "is_v15_hard_fail" in _func_names(_SRC_V15)

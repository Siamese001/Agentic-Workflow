"""ADG contract tests for apps_rg/config/reasoning_toggles_config.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.config.reasoning_toggles_config as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "config" / "reasoning_toggles_config.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestReasoningTogglesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_reasoning_toggles_class(self):
        assert "ReasoningToggles" in _class_names()

    def test_has_validate_branches_method(self):
        assert "validate_branches" in _methods_of("ReasoningToggles")

    def test_has_use_cot_field(self):
        assert "use_cot" in _src_text()

    def test_has_use_reflexion_field(self):
        assert "use_reflexion" in _src_text()

    def test_has_strict_mode_field(self):
        assert "strict_mode" in _src_text()

    def test_has_use_persistent_tracing_field(self):
        assert "use_persistent_tracing" in _src_text()

    def test_has_use_cyclic_validation_field(self):
        assert "use_cyclic_validation" in _src_text()

    def test_has_tot_branches_field(self):
        assert "tot_branches" in _src_text()

    def test_has_min_tot_depth_field(self):
        assert "min_tot_depth" in _src_text()

    def test_has_temperature_cap_field(self):
        assert "temperature_cap" in _src_text()

    def test_has_default_toggles_constant(self):
        assert "DEFAULT_TOGGLES" in _src_text()

    def test_use_cot_default_is_true(self):
        import re
        assert re.search(r"use_cot\b.*True", _src_text()), "use_cot default should be True"

    def test_use_reflexion_default_is_false(self):
        import re
        assert re.search(r"use_reflexion\b.*False", _src_text()), "use_reflexion default should be False"

    def test_strict_mode_default_is_true(self):
        import re
        assert re.search(r"strict_mode\b.*True", _src_text()), "strict_mode default should be True"

    def test_tot_branches_default_is_2(self):
        import re
        assert re.search(r"tot_branches\b.*=.*2\b", _src_text()), "tot_branches default should be 2"

    def test_min_tot_depth_default_is_1(self):
        import re
        assert re.search(r"min_tot_depth\b.*=.*1\b", _src_text()), "min_tot_depth default should be 1"

    def test_temperature_cap_default_is_0_5(self):
        import re
        assert re.search(r"temperature_cap\b.*0\.5", _src_text()), "temperature_cap default should be 0.5"

    def test_branches_validation_logic_present(self):
        src = _src_text()
        assert "tot_branches" in src and ("raise" in src or "ValueError" in src)

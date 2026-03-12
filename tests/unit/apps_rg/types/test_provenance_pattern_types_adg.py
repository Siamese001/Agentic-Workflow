"""ADG contract tests for apps_rg/types/provenance_pattern_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.types.provenance_pattern_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "provenance_pattern_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set[str]:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


class TestProvenancePatternTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_provenance_pattern(self):
        assert "ProvenancePattern" in _class_names()

    def test_has_bullet_provenance_log(self):
        assert "BulletProvenanceLog" in _class_names()

    def test_has_bullet_synthesizer_config(self):
        assert "BulletSynthesizerConfig" in _class_names()

    def test_has_bullet_synthesizer_result(self):
        assert "BulletSynthesizerResult" in _class_names()

    def test_synthesizer_config_has_min_words(self):
        assert "min_words" in _methods_of("BulletSynthesizerConfig")

    def test_synthesizer_config_has_max_words(self):
        assert "max_words" in _methods_of("BulletSynthesizerConfig")

    def test_provenance_pattern_has_str(self):
        assert "__str__" in _methods_of("ProvenancePattern")

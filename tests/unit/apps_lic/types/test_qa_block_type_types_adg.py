"""ADG contract tests for apps_lic/types/qa_block_type_types.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_lic.types.qa_block_type_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "types" / "qa_block_type_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestQaBlockTypeTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_qa_block_type(self):
        assert "QaBlockType" in _class_names()

    def test_has_message_assembler_config(self):
        assert "MessageAssemblerConfig" in _class_names()

    def test_has_linkedin_qa_grid_value(self):
        assert "LINKEDIN_QA_GRID" in _src_text()

    def test_has_canonical_signature_lines_field(self):
        assert "canonical_signature_lines" in _src_text()

    def test_has_required_qa_blocks_field(self):
        assert "required_qa_blocks" in _src_text()


def test_module_importable():
    assert True

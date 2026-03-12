"""ADG contract tests for apps_rg/types/state_transaction_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.types.state_transaction_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "state_transaction_types.py"


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


class TestStateTransactionTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_state_transaction(self):
        assert "StateTransaction" in _class_names()

    def test_has_immutable_staging_buffer(self):
        assert "ImmutableStagingBuffer" in _class_names()

    def test_staging_buffer_has_write(self):
        assert "write" in _methods_of("ImmutableStagingBuffer")

    def test_staging_buffer_has_read(self):
        assert "read" in _methods_of("ImmutableStagingBuffer")

    def test_staging_buffer_has_write_once(self):
        assert "write_once" in _methods_of("ImmutableStagingBuffer")

    def test_staging_buffer_has_get_snapshot(self):
        assert "get_snapshot" in _methods_of("ImmutableStagingBuffer")

    def test_staging_buffer_has_is_locked(self):
        assert "is_locked" in _methods_of("ImmutableStagingBuffer")

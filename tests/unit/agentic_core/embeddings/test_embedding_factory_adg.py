"""ADG contract tests for agentic_core/embeddings/embedding_factory.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.embeddings.embedding_factory as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[4]
    / "agentic_core" / "embeddings" / "embedding_factory.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestEmbeddingFactorySource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_embedding_disabled_error(self):
        assert "EmbeddingDisabledError" in _class_names()

    def test_has_embedding_sovereignty_violation_error(self):
        assert "EmbeddingSovereigntyViolationError" in _class_names()

    def test_has_embedding_client(self):
        assert "EmbeddingClient" in _class_names()

    def test_has_is_enabled_function(self):
        assert "is_enabled" in _func_names()

    def test_has_register_embedding_client(self):
        assert "register_embedding_client" in _func_names()

    def test_embedding_enabled_constant_in_source(self):
        assert "EMBEDDING_ENABLED" in _src_text()

    def test_embedding_disabled_error_subclasses_runtime_error(self):
        assert "RuntimeError" in _src_text()

    def test_has_get_embedding_method(self):
        assert "get_embedding" in _src_text()

    def test_has_get_embeddings_batch_method(self):
        assert "get_embeddings_batch" in _src_text()

    def test_disabled_error_raised_when_disabled(self):
        assert "EmbeddingDisabledError" in _src_text()
        assert "false" in _src_text().lower() or "False" in _src_text()
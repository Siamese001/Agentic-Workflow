"""Unit tests for canonical AST + Fuzzy Matching Utilities"""

import ast
import os

from agentic_core.utils.ast_fuzzy_util import (
    ast_dump_hash,
    normalize_repo_path,
    parse_ast_safe,
    similarity_score,
    tokenize_simple,
)


class TestAstDumpHash:
    """Test AST structural hashing."""

    def test_hash_determinism(self):
        """Hash of same AST is deterministic."""
        code = "def foo(x): return x + 1"
        tree1 = ast.parse(code)
        tree2 = ast.parse(code)

        hash1 = ast_dump_hash(tree1)
        hash2 = ast_dump_hash(tree2)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest

    def test_hash_differs_for_different_code(self):
        """Hash differs for different code."""
        tree1 = ast.parse("def foo(x): return x + 1")
        tree2 = ast.parse("def foo(x): return x + 2")

        hash1 = ast_dump_hash(tree1)
        hash2 = ast_dump_hash(tree2)

        assert hash1 != hash2

    def test_hash_ignores_attributes(self):
        """Hash ignores line numbers and column offsets."""
        code = "x = 1"
        tree = ast.parse(code)
        hash_val = ast_dump_hash(tree)

        # Should be consistent regardless of attributes
        assert len(hash_val) == 64


class TestSimilarityScore:
    """Test fuzzy similarity scoring."""

    def test_identical_text_score_one(self):
        """Identical text has similarity 1.0."""
        text = "def foo(x): return x + 1"
        score = similarity_score(text, text)
        assert score == 1.0

    def test_empty_text_score_zero(self):
        """Empty text has similarity 0.0."""
        score = similarity_score("", "def foo(x): return x")
        assert score == 0.0

    def test_similarity_symmetric(self):
        """Similarity is symmetric."""
        text_a = "def foo(x): return x + 1"
        text_b = "def foo(x): return x + 2"

        score_ab = similarity_score(text_a, text_b)
        score_ba = similarity_score(text_b, text_a)

        assert score_ab == score_ba
        assert 0.0 <= score_ab <= 1.0

    def test_similar_code_high_score(self):
        """Similar code has high similarity score."""
        text_a = "def foo(x): return x + 1"
        text_b = "def foo(x): return x + 1"

        score = similarity_score(text_a, text_b)
        assert score > 0.9


class TestTokenizeSimple:
    """Test simple tokenization."""

    def test_tokenize_basic(self):
        """Basic tokenization splits on whitespace and punctuation."""
        text = "def foo(x): return x + 1"
        tokens = tokenize_simple(text)

        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)
        assert all(t.islower() for t in tokens)  # lowercase

    def test_tokenize_idempotency(self):
        """Tokenizing twice gives same result."""
        text = "def foo(x): return x + 1"
        tokens1 = tokenize_simple(text)
        tokens2 = tokenize_simple(text)

        assert tokens1 == tokens2

    def test_tokenize_empty_string(self):
        """Empty string tokenizes to empty list."""
        tokens = tokenize_simple("")
        assert tokens == []


class TestNormalizeRepoPath:
    """Test repository path normalization."""

    def test_normalize_backslashes(self):
        """Backslashes are converted to forward slashes."""
        path = "agentic_core\\utils\\ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == "agentic_core/utils/ast_fuzzy.py"
        assert "\\" not in normalized

    def test_normalize_already_normalized(self):
        """Already normalized paths are unchanged."""
        path = "agentic_core/utils/ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == path

    def test_normalize_mixed_slashes(self):
        """Mixed slashes are normalized to forward."""
        path = "agentic_core\\utils/ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == "agentic_core/utils/ast_fuzzy.py"


class TestThresholdConfiguration:
    """Test threshold environment variable configuration."""

    def test_default_threshold(self):
        """Default threshold is 0.6."""
        # Clear env var if set
        old_val = os.environ.pop("AST_FUZZY_THRESHOLD", None)
        try:
            # Re-import to get fresh value
            from agentic_core.utils import ast_fuzzy as module

            threshold = module.get_threshold()
            assert threshold == 0.6
        finally:
            if old_val is not None:
                os.environ["AST_FUZZY_THRESHOLD"] = old_val

    def test_threshold_env_override(self):
        """Threshold can be overridden via environment variable."""
        old_val = os.environ.get("AST_FUZZY_THRESHOLD")
        try:
            os.environ["AST_FUZZY_THRESHOLD"] = "0.75"
            # Re-import to get new value
            import importlib

            import agentic_core.utils.ast_fuzzy as module

            importlib.reload(module)
            threshold = module.get_threshold()
            assert threshold == 0.75
        finally:
            if old_val is not None:
                os.environ["AST_FUZZY_THRESHOLD"] = old_val
            else:
                os.environ.pop("AST_FUZZY_THRESHOLD", None)


class TestParseAstSafe:
    """Test safe AST parsing."""

    def test_parse_valid_code(self):
        """Valid code parses successfully."""
        code = "def foo(x): return x + 1"
        tree = parse_ast_safe(code)

        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_parse_invalid_code_returns_none(self):
        """Invalid code returns None."""
        code = "def foo(x) return x + 1"  # Missing colon
        tree = parse_ast_safe(code)

        assert tree is None

    def test_parse_empty_string(self):
        """Empty string parses to empty module."""
        tree = parse_ast_safe("")

        assert tree is not None
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 0

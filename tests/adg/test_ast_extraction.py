"""Test AstExtraction functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAstExtraction:
    """Test AstExtraction functionality."""

    def test_ast_extraction_imports(self):
        """Test AST extraction module imports."""
        from tools import ast_extraction
        assert ast_extraction is not None

    def test_ast_extractor_class(self):
        """Test AST extractor class exists."""
        from tools.ast_extraction import ASTExtractor
        assert ASTExtractor is not None

    def test_extract_ast(self):
        """Test extract AST function."""
        from tools.ast_extraction import extract_ast
        assert callable(extract_ast)

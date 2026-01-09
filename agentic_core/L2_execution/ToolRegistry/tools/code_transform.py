"""
Code Transform tool for L2 Execution.

Provides code transformation utilities.
"""
from typing import Any, Dict, List, Optional
import ast
import logging

logger = logging.getLogger(__name__)


class CodeTransformer:
    """Tool for transforming code."""
    
    def __init__(self):
        self._transformations: List[callable] = []
    
    def add_transformation(self, transform: callable) -> None:
        """Add a transformation function."""
        self._transformations.append(transform)
    
    def transform(self, code: str) -> str:
        """Apply all transformations to code."""
        result = code
        for transform in self._transformations:
            result = transform(result)
        return result
    
    def parse(self, code: str) -> ast.AST:
        """Parse code into AST."""
        return ast.parse(code)
    
    def unparse(self, tree: ast.AST) -> str:
        """Convert AST back to code."""
        return ast.unparse(tree)


__all__ = ['CodeTransformer']

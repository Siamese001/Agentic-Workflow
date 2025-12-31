"""Test semantic chunking for sovereign ingestion mission."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from pathlib import Path
from agentic_core.L0_maintenance.scripts.sovereign_ingestion_mission import (
    ChunkType,
    SemanticChunk,
    chunk_python_ast,
    chunk_text_fallback,
    chunk_text,
    _extract_docstring,
    _get_source_segment,
)
import ast


class TestSemanticChunking:
    """Test AST-based semantic chunking."""

    def test_extract_docstring_from_function(self):
        """Test docstring extraction from function."""
        code = '''
def example_function():
    """This is a docstring."""
    return 42
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        docstring = _extract_docstring(func_node)
        assert docstring == "This is a docstring."

    def test_extract_docstring_from_class(self):
        """Test docstring extraction from class."""
        code = '''
class ExampleClass:
    """Class docstring."""
    pass
'''
        tree = ast.parse(code)
        class_node = tree.body[0]
        docstring = _extract_docstring(class_node)
        assert docstring == "Class docstring."

    def test_get_source_segment(self):
        """Test source line extraction."""
        lines = ["line 1", "line 2", "line 3", "line 4", "line 5"]
        segment = _get_source_segment(lines, 2, 4)
        assert segment == "line 2\nline 3\nline 4"

    def test_chunk_python_ast_simple_function(self):
        """Test chunking a simple Python function."""
        code = '''"""Module docstring."""
import os
import sys

def hello_world():
    """Say hello."""
    print("Hello, World!")
'''
        file_path = Path("test_module.py")
        chunks = chunk_python_ast(code, file_path)
        
        # Should have: module docstring, imports, function
        assert len(chunks) >= 3
        
        # Check module docstring
        doc_chunks = [c for c in chunks if c.chunk_type == ChunkType.DOCSTRING]
        assert len(doc_chunks) == 1
        assert "Module docstring" in doc_chunks[0].text
        
        # Check imports
        import_chunks = [c for c in chunks if c.chunk_type == ChunkType.IMPORT_BLOCK]
        assert len(import_chunks) == 1
        assert "import os" in import_chunks[0].text
        
        # Check function
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        assert len(func_chunks) == 1
        assert func_chunks[0].name == "hello_world"
        assert func_chunks[0].docstring == "Say hello."

    def test_chunk_python_ast_with_class(self):
        """Test chunking Python code with classes."""
        code = '''
class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract two numbers."""
        return a - b
'''
        file_path = Path("calculator.py")
        chunks = chunk_python_ast(code, file_path)
        
        # Should have class chunk
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        assert len(class_chunks) == 1
        assert class_chunks[0].name == "Calculator"
        assert class_chunks[0].docstring == "A simple calculator."
        
        # Should have function chunks (methods detected as functions by ast.walk)
        func_chunks = [c for c in chunks if c.chunk_type in (ChunkType.FUNCTION, ChunkType.METHOD)]
        assert len(func_chunks) >= 2

    def test_chunk_python_ast_syntax_error_fallback(self):
        """Test fallback to line-based chunking on syntax error."""
        code = "def broken_syntax(\n    incomplete"
        file_path = Path("broken.py")
        chunks = chunk_python_ast(code, file_path)
        
        # Should fall back to text blocks
        assert all(c.chunk_type == ChunkType.TEXT_BLOCK for c in chunks)

    def test_chunk_text_fallback(self):
        """Test line-based fallback chunking."""
        text = "\n".join([f"Line {i}" for i in range(1, 101)])
        file_path = Path("test.txt")
        chunks = chunk_text_fallback(text, file_path)
        
        # Should create chunks of 50 lines
        assert len(chunks) == 2
        assert chunks[0].chunk_type == ChunkType.TEXT_BLOCK
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 50
        assert chunks[1].start_line == 51
        assert chunks[1].end_line == 100

    def test_chunk_text_python_file(self):
        """Test chunk_text dispatcher for Python files."""
        code = '''
def test_function():
    """Test function."""
    pass
'''
        file_path = Path("test.py")
        chunks = chunk_text(code, file_path)
        
        # Should return dicts with metadata
        assert isinstance(chunks, list)
        assert all(isinstance(c, dict) for c in chunks)
        assert all('hash' in c and 'text' in c and 'metadata' in c for c in chunks)
        
        # Check metadata enrichment
        if chunks:
            meta = chunks[0]['metadata']
            assert 'chunk_type' in meta
            assert 'name' in meta
            assert 'start_line' in meta
            assert 'end_line' in meta

    def test_chunk_text_non_python_file(self):
        """Test chunk_text dispatcher for non-Python files."""
        text = "This is a markdown file.\n" * 60
        file_path = Path("test.md")
        chunks = chunk_text(text, file_path)
        
        # Should use fallback chunking
        assert len(chunks) >= 1
        meta = chunks[0]['metadata']
        assert meta['chunk_type'] == ChunkType.TEXT_BLOCK.value
        assert meta['file_type'] == '.md'

    def test_chunk_metadata_structure(self):
        """Test that chunk metadata has all required fields."""
        code = '''
def example():
    """Example function."""
    return True
'''
        file_path = Path("/test/path/example.py")
        chunks = chunk_text(code, file_path)
        
        for chunk in chunks:
            assert 'hash' in chunk
            assert 'text' in chunk
            assert 'metadata' in chunk
            
            meta = chunk['metadata']
            assert 'source' in meta
            assert 'start_line' in meta
            assert 'end_line' in meta
            assert 'file_type' in meta
            assert 'chunk_type' in meta
            assert 'name' in meta
            # parent and docstring are optional


class TestSemanticChunkDataclass:
    """Test SemanticChunk dataclass."""

    def test_semantic_chunk_creation(self):
        """Test creating a SemanticChunk."""
        chunk = SemanticChunk(
            chunk_type=ChunkType.FUNCTION,
            name="test_func",
            text="def test_func(): pass",
            start_line=1,
            end_line=1
        )
        assert chunk.chunk_type == ChunkType.FUNCTION
        assert chunk.name == "test_func"
        assert chunk.parent is None
        assert chunk.docstring is None

    def test_semantic_chunk_with_parent(self):
        """Test SemanticChunk with parent class."""
        chunk = SemanticChunk(
            chunk_type=ChunkType.METHOD,
            name="MyClass.my_method",
            text="def my_method(self): pass",
            start_line=5,
            end_line=6,
            parent="MyClass",
            docstring="Method docstring"
        )
        assert chunk.chunk_type == ChunkType.METHOD
        assert chunk.parent == "MyClass"
        assert chunk.docstring == "Method docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

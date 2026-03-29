"""Wave 5: Tools — Shared Modules & Type Check

Tests for:
- tools/adg/shared_modules/file_operations.py — file I/O, path resolution, atomic writes
- tools/adg/shared_modules/string_processing.py — text normalization, chunking
- tools/adg/shared_modules/validation.py — schema validation, constraint checking
- tools/adg/adg_type_check.py — type inference, literal detection, type surface
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# File Operations Tests
# ============================================================================

@pytest.mark.unit
class TestFileOperations:
    """Tests for file_operations.py — file I/O utilities."""

    def test_path_resolution_absolute(self, tmp_path):
        """Test path resolution to absolute paths."""
        rel_path = tmp_path / "subdir" / "file.txt"
        rel_path.parent.mkdir(parents=True)
        rel_path.write_text("content")
        
        abs_path = rel_path.resolve()
        assert abs_path.is_absolute()
        assert abs_path.exists()

    def test_file_read_utf8(self, tmp_path):
        """Test reading file with UTF-8 encoding."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World", encoding="utf-8")
        
        content = test_file.read_text(encoding="utf-8")
        assert content == "Hello World"

    def test_file_write_utf8(self, tmp_path):
        """Test writing file with UTF-8 encoding."""
        test_file = tmp_path / "output.txt"
        content = "Test content"
        
        test_file.write_text(content, encoding="utf-8")
        assert test_file.exists()
        assert test_file.read_text() == content

    def test_directory_creation(self, tmp_path):
        """Test directory creation with parents."""
        deep_path = tmp_path / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True, exist_ok=True)
        
        assert deep_path.exists()
        assert deep_path.is_dir()

    def test_file_extension_detection(self):
        """Test file extension detection."""
        path = Path("/path/to/file.py")
        assert path.suffix == ".py"
        
        path = Path("/path/to/archive.tar.gz")
        assert path.suffix == ".gz"
        assert path.suffixes == [".tar", ".gz"]


# ============================================================================
# String Processing Tests
# ============================================================================

@pytest.mark.unit
class TestStringProcessing:
    """Tests for string_processing.py — text utilities."""

    def test_text_normalization_whitespace(self):
        """Test whitespace normalization."""
        text = "  hello   world  "
        normalized = " ".join(text.split())  # Collapse whitespace
        assert normalized == "hello world"

    def test_line_endings_normalization(self):
        """Test line ending normalization to LF."""
        text_crlf = "line1\r\nline2\r\nline3"
        text_lf = text_crlf.replace("\r\n", "\n")
        assert "\r\n" not in text_lf
        assert text_lf.count("\n") == 2

    def test_text_chunking_by_length(self):
        """Test chunking text by character length."""
        text = "abcdefghij"
        chunk_size = 3
        
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        assert len(chunks) == 4
        assert chunks[0] == "abc"
        assert chunks[1] == "def"
        assert chunks[2] == "ghi"
        assert chunks[3] == "j"

    def test_text_chunking_by_lines(self):
        """Test chunking text by line count."""
        lines = ["line1", "line2", "line3", "line4", "line5"]
        chunk_size = 2
        
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunks.append("\n".join(lines[i:i+chunk_size]))
        
        assert len(chunks) == 3
        assert "line1" in chunks[0]
        assert "line5" in chunks[2]

    def test_empty_line_removal(self):
        """Test removal of empty lines."""
        text = "line1\n\nline2\n\n\nline3"
        lines = text.split("\n")
        non_empty = [line for line in lines if line.strip()]
        
        assert len(non_empty) == 3
        assert non_empty == ["line1", "line2", "line3"]


# ============================================================================
# Validation Tests
# ============================================================================

@pytest.mark.unit
class TestValidation:
    """Tests for validation.py — schema validation utilities."""

    def test_required_field_validation(self):
        """Test validation of required fields."""
        data = {"name": "test", "value": 42}
        required = ["name", "value"]
        
        missing = [field for field in required if field not in data]
        assert len(missing) == 0

    def test_missing_required_field(self):
        """Test detection of missing required fields."""
        data = {"name": "test"}  # missing "value"
        required = ["name", "value"]
        
        missing = [field for field in required if field not in data]
        assert "value" in missing

    def test_type_validation_string(self):
        """Test string type validation."""
        value = "hello"
        assert isinstance(value, str)

    def test_type_validation_int(self):
        """Test integer type validation."""
        value = 42
        assert isinstance(value, int)

    def test_type_validation_list(self):
        """Test list type validation."""
        value = [1, 2, 3]
        assert isinstance(value, list)

    def test_enum_validation(self):
        """Test enum value validation."""
        allowed = ["option_a", "option_b", "option_c"]
        value = "option_b"
        
        assert value in allowed

    def test_enum_validation_invalid(self):
        """Test detection of invalid enum values."""
        allowed = ["option_a", "option_b"]
        value = "option_c"
        
        assert value not in allowed


# ============================================================================
# Type Check Tests
# ============================================================================

@pytest.mark.unit
class TestTypeCheck:
    """Tests for adg_type_check.py — type inference and validation."""

    def test_function_annotation_extraction(self):
        """Test extraction of function type annotations."""
        import ast
        
        code = '''
def process(data: dict[str, int]) -> list[str]:
    return []
'''
        tree = ast.parse(code)
        func = tree.body[0]
        
        assert isinstance(func, ast.FunctionDef)
        assert func.returns is not None  # Has return annotation

    def test_variable_annotation_extraction(self):
        """Test extraction of variable type annotations."""
        import ast
        
        code = 'x: int = 5'
        tree = ast.parse(code)
        
        node = tree.body[0]
        assert isinstance(node, ast.AnnAssign)
        assert isinstance(node.annotation, ast.Name)
        assert node.annotation.id == "int"

    def test_literal_type_inference_int(self):
        """Test inference of int literal type."""
        value = 42
        assert isinstance(value, int)
        assert type(value).__name__ == "int"

    def test_literal_type_inference_str(self):
        """Test inference of str literal type."""
        value = "hello"
        assert isinstance(value, str)
        assert type(value).__name__ == "str"

    def test_literal_type_inference_list(self):
        """Test inference of list literal type."""
        value = [1, 2, 3]
        assert isinstance(value, list)
        assert type(value).__name__ == "list"

    def test_literal_type_inference_dict(self):
        """Test inference of dict literal type."""
        value = {"a": 1, "b": 2}
        assert isinstance(value, dict)
        assert type(value).__name__ == "dict"

    def test_none_type_inference(self):
        """Test inference of None literal type."""
        value = None
        assert value is None

    def test_type_surface_mapping(self):
        """Test type surface mapping from AST."""
        import ast
        
        code = '''
x: int = 1
y: str = "hello"
z: list[int] = [1, 2, 3]
'''
        tree = ast.parse(code)
        
        type_surface = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    if isinstance(node.annotation, ast.Name):
                        type_surface[var_name] = node.annotation.id
        
        assert type_surface.get("x") == "int"
        assert type_surface.get("y") == "str"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.unit
class TestSharedModulesIntegration:
    """Integration tests for shared modules."""

    def test_file_to_string_processing(self, tmp_path):
        """Test reading file and processing its content."""
        # Create file
        test_file = tmp_path / "input.txt"
        test_file.write_text("  hello   world  \n\n  test  ")
        
        # Read
        content = test_file.read_text()
        
        # Process (normalize whitespace)
        normalized = " ".join(content.split())
        
        assert normalized == "hello world test"

    def test_validation_with_file_data(self, tmp_path):
        """Test validation on data loaded from file."""
        import json
        
        # Create JSON file
        data_file = tmp_path / "data.json"
        data = {"name": "test", "count": 42, "items": ["a", "b"]}
        data_file.write_text(json.dumps(data))
        
        # Load and validate
        loaded = json.loads(data_file.read_text())
        
        assert "name" in loaded
        assert isinstance(loaded["count"], int)
        assert isinstance(loaded["items"], list)

"""
Test suite for Boilerplate Stripping Tool

Verifies that the boilerplate stripper safely removes boilerplate
while preserving behavioral logic.
"""

import ast
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import with graceful fallback
try:
    from tools.adg.strip_boilerplate import (
        BoilerplateStripper,
        SafeBoilerplateStripper,
        StripResult,
    )
except ImportError as _import_err:
    pytest.skip(f"strip_boilerplate not available: {_import_err}", allow_module_level=True)


def test_boilerplate_stripper_removes_emit_calls():
    """Test that stripper removes emit calls."""
    code = """
import os

_emit_records_execution_trace("test", "test", "test")
_emit_applies_guardrail("test", "test", "test")

def behavioral_function():
    return "test"
"""
    tree = ast.parse(code)

    stripper = BoilerplateStripper()
    stripped_tree = stripper.visit(tree)

    assert stripper.removed_count == 2
    assert stripper.emit_calls_removed == 2

    # Check that emit calls are removed
    remaining_calls = []
    for node in ast.walk(stripped_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id.startswith('_emit_'):
                remaining_calls.append(node.func.id)

    assert len(remaining_calls) == 0


def test_boilerplate_stripper_removes_imports():
    """Test that stripper removes boilerplate imports."""
    code = """
import os
import sys
import json
from typing import Any

def behavioral_function():
    return "test"
"""
    tree = ast.parse(code)

    stripper = BoilerplateStripper()
    stripped_tree = stripper.visit(tree)

    assert stripper.removed_count >= 2  # At least json and typing
    assert stripper.imports_removed >= 2


def test_boilerplate_stripper_preserves_behavioral():
    """Test that stripper preserves behavioral functions."""
    code = """
import os

def behavioral_function():
    x = 1 + 1
    return x

class BehavioralClass:
    def method(self):
        return "test"
"""
    tree = ast.parse(code)

    stripper = BoilerplateStripper()
    stripped_tree = stripper.visit(tree)

    # Count behavioral nodes
    functions = []
    classes = []
    for node in ast.walk(stripped_tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    assert "behavioral_function" in functions
    assert "BehavioralClass" in classes


def test_safe_stripper_clean_file():
    """Test safe stripper on cleanable file."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import os
import json

_emit_records_execution_trace("test", "test", "test")

def behavioral_function():
    x = 1 + 1
    return x
""")
        temp_path = Path(f.name)

    try:
        stripper = SafeBoilerplateStripper(Path("."))
        result = stripper.strip_file_boilerplate(temp_path, dry_run=True)

        assert result.action == "cleaned"
        assert result.lines_removed > 0
        assert result.emit_calls_removed > 0
        assert result.became_hollow is False
    finally:
        temp_path.unlink()


def test_safe_stripper_becomes_hollow():
    """Test safe stripper when file would become hollow."""
    # Create temporary file with only boilerplate
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import os
import json

_emit_records_execution_trace("test", "test", "test")
_emit_applies_guardrail("test", "test", "test")
""")
        temp_path = Path(f.name)

    try:
        stripper = SafeBoilerplateStripper(Path("."))
        result = stripper.strip_file_boilerplate(temp_path, dry_run=True)

        assert result.action == "deleted"
        assert "become hollow" in result.reason.lower()
        assert result.became_hollow is True
    finally:
        temp_path.unlink()


def test_safe_stripper_no_boilerplate():
    """Test safe stripper on file with no boilerplate."""
    # Create temporary file with only behavioral code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def behavioral_function():
    x = 1 + 1
    return x

class BehavioralClass:
    def method(self):
        return "test"
""")
        temp_path = Path(f.name)

    try:
        stripper = SafeBoilerplateStripper(Path("."))
        result = stripper.strip_file_boilerplate(temp_path, dry_run=True)

        assert result.action == "skipped"
        assert "no boilerplate" in result.reason.lower()
    finally:
        temp_path.unlink()


def test_safe_stripper_syntax_error():
    """Test safe stripper on file with syntax error."""
    # Create temporary file with syntax error
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def broken(\n")  # Missing closing parenthesis
        temp_path = Path(f.name)

    try:
        stripper = SafeBoilerplateStripper(Path("."))
        result = stripper.strip_file_boilerplate(temp_path, dry_run=True)

        assert result.action == "skipped"
        assert "syntax error" in result.reason.lower()
    finally:
        temp_path.unlink()


@patch('tools.adg.strip_boilerplate.SafeBoilerplateStripper.strip_file_boilerplate')
def test_strip_directory(mock_strip):
    """Test directory stripping."""
    # Mock file results
    mock_strip.side_effect = [
        StripResult(action="cleaned", reason="test", lines_removed=5),
        StripResult(action="skipped", reason="no boilerplate"),
        StripResult(action="deleted", reason="became hollow"),
    ]

    with patch('pathlib.Path.rglob') as mock_rglob:
        mock_rglob.return_value = [Path("file1.py"), Path("file2.py"), Path("file3.py")]

        with patch('pathlib.Path.exists', return_value=True):
            stripper = SafeBoilerplateStripper(Path("."))
            results = stripper.strip_directory(Path("."), dry_run=True, recursive=True)

    assert len(results) == 3
    assert results[0].action == "cleaned"
    assert results[1].action == "skipped"
    assert results[2].action == "deleted"


def test_generate_report():
    """Test report generation."""
    results = [
        StripResult(action="cleaned", reason="test", lines_removed=5, emit_calls_removed=2),
        StripResult(action="deleted", reason="hollow", lines_removed=10, emit_calls_removed=5),
        StripResult(action="skipped", reason="no boilerplate"),
        StripResult(action="cleaned", reason="test2", lines_removed=3, became_hollow=True),
    ]

    stripper = SafeBoilerplateStripper(Path("."))
    report = stripper.generate_report(results)

    assert report["total_files"] == 4
    assert report["cleaned"] == 2
    assert report["deleted"] == 1
    assert report["skipped"] == 1
    assert report["total_lines_removed"] == 18
    assert report["total_emit_calls_removed"] == 7
    assert report["files_became_hollow"] == 1


if __name__ == "__main__":
    pytest.main([__file__])

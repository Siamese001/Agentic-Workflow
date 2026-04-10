"""
Test suite for Zero-Loss Refactor Verifier

Verifies that the zero-loss refactor verifier correctly detects
neutered files and generates appropriate cleanup commands.
"""

import ast
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ops_scripts.ci.zero_loss_refactor_verifier import (
    check_file_neutered,
    check_files_neutered,
    count_behavioral_nodes,
    generate_cleanup_commands,
)


def test_count_behavioral_nodes():
    """Test behavioral node counting."""
    code = """
import os

def behavioral_function():
    x = 1 + 1
    return x

class BehavioralClass:
    def method(self):
        return "test"

def _emit_boilerplate():
    pass
"""
    tree = ast.parse(code)
    count = count_behavioral_nodes(tree)
    assert count == 2  # 1 function + 1 class


def test_count_behavioral_nodes_empty():
    """Test behavioral node counting on empty file."""
    tree = ast.parse("")
    count = count_behavioral_nodes(tree)
    assert count == 0


def test_count_behavioral_nodes_only_boilerplate():
    """Test behavioral node counting on boilerplate-only file."""
    code = """
import os
import sys

_emit_records_execution_trace("test", "test", "test")
_emit_applies_guardrail("test", "test", "test")
"""
    tree = ast.parse(code)
    count = count_behavioral_nodes(tree)
    assert count == 0


def test_check_file_neutered_became_hollow():
    """Test detection of neutered file."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write hollow content
        f.write("""
import os

_emit_records_execution_trace("test", "test", "test")
""")
        temp_path = Path(f.name)

    try:
        # Mock git_show to return behavioral content
        with patch('ops_scripts.ci.zero_loss_refactor_verifier.git_show') as mock_git_show:
            mock_git_show.return_value = """
def behavioral_function():
    x = 1 + 1
    return x
"""

            is_neutered, before_count, after_count = check_file_neutered(temp_path, "HEAD~1")

            assert is_neutered is True
            assert before_count == 1
            assert after_count == 0
    finally:
        temp_path.unlink()


def test_check_file_neutered_not_neutered():
    """Test file that retained behavioral content."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write content with behavioral function
        f.write("""
import os

def behavioral_function():
    x = 1 + 1
    return x
""")
        temp_path = Path(f.name)

    try:
        # Mock git_show to return same content
        with patch('ops_scripts.ci.zero_loss_refactor_verifier.git_show') as mock_git_show:
            mock_git_show.return_value = """
import os

def behavioral_function():
    x = 1 + 1
    return x
"""

            is_neutered, before_count, after_count = check_file_neutered(temp_path, "HEAD~1")

            assert is_neutered is False
            assert before_count == 1
            assert after_count == 1
    finally:
        temp_path.unlink()


def test_check_file_neutered_was_always_hollow():
    """Test file that was always hollow (not neutered)."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write hollow content
        f.write("""
import os
_emit_records_execution_trace("test", "test", "test")
""")
        temp_path = Path(f.name)

    try:
        # Mock git_show to return hollow content
        with patch('ops_scripts.ci.zero_loss_refactor_verifier.git_show') as mock_git_show:
            mock_git_show.return_value = """
import os
_emit_records_execution_trace("test", "test", "test")
"""

            is_neutered, before_count, after_count = check_file_neutered(temp_path, "HEAD~1")

            assert is_neutered is False  # Was always hollow
            assert before_count == 0
            assert after_count == 0
    finally:
        temp_path.unlink()


@patch('ops_scripts.ci.zero_loss_refactor_verifier.get_modified_files_since')
def test_check_files_neutered(mock_get_modified):
    """Test checking multiple files for neutered content."""
    mock_get_modified.return_value = [Path("file1.py"), Path("file2.py")]

    # Create temporary files
    temp_files = []
    for i in range(2):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            if i == 0:
                # File 1: became hollow
                f.write("import os\n")
            else:
                # File 2: still has content
                f.write("""
def test():
    pass
""")
            temp_files.append(Path(f.name))

    try:
        # Mock git_show
        with patch('ops_scripts.ci.zero_loss_refactor_verifier.git_show') as mock_git_show:
            def git_show_side_effect(commit_hash, file_path):
                if file_path == temp_files[0]:
                    return "def test():\n    pass\n"
                else:
                    return "def test():\n    pass\n"

            mock_git_show.side_effect = git_show_side_effect

            # Override the file paths in results
            results = check_files_neutered(temp_files, "HEAD~1")

            # Check results
            assert len(results) == 2
            assert results[temp_files[0]]["neutered"] is True
            assert results[temp_files[1]]["neutered"] is False
    finally:
        for f in temp_files:
            f.unlink()


def test_generate_cleanup_commands():
    """Test generation of cleanup commands."""
    neutered_files = [
        Path("test/file1.py"),
        Path("test/file2.py"),
    ]

    commands = generate_cleanup_commands(neutered_files)

    assert len(commands) == 4  # 2 files * 2 commands each
    assert "git rm test/file1.py" in commands
    assert "git rm test/file2.py" in commands
    assert "# Removed hollow file: test/file1.py" in commands
    assert "# Removed hollow file: test/file2.py" in commands


def test_generate_cleanup_commands_empty():
    """Test generation of cleanup commands with no files."""
    commands = generate_cleanup_commands([])
    assert commands == []


if __name__ == "__main__":
    pytest.main([__file__])

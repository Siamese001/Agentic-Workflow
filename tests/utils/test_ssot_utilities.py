"""
Pytest suite for ProjectRoot and FileUtils SSOT utilities.

Tests verify that:
- Project root is detected via marker files
- Atomic write and safe read work correctly
- Directory creation works
"""
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.project_root import get_project_root, clear_project_root_cache
from agentic_core.utils.file_utils import (
    safe_read_file, 
    safe_write_file, 
    ensure_directory,
    safe_delete_file,
    safe_copy_file,
)


def test_project_root_detection(tmp_path):
    """Verify root is detected via marker files."""
    # Clear cache before test
    clear_project_root_cache()
    
    # Create a fake project structure
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "pyproject.toml").touch()
    
    # Create a deep subdirectory
    deep_dir = tmp_path / "agentic_core" / "deep" / "nested" / "dir"
    deep_dir.mkdir(parents=True)
    
    # Act
    root = get_project_root(start_path=str(deep_dir))
    
    # Assert
    assert root == tmp_path
    
    # Clear cache after test
    clear_project_root_cache()


def test_project_root_from_file(tmp_path):
    """Verify root detection works when starting from a file path."""
    # Clear cache before test
    clear_project_root_cache()
    
    # Create a fake project structure
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "pyproject.toml").touch()
    
    # Create a file in a subdirectory
    subdir = tmp_path / "agentic_core" / "utils"
    subdir.mkdir(parents=True)
    test_file = subdir / "test_file.py"
    test_file.touch()
    
    # Act - start from a file path
    root = get_project_root(start_path=str(test_file))
    
    # Assert
    assert root == tmp_path
    
    # Clear cache after test
    clear_project_root_cache()


def test_safe_file_io(tmp_path):
    """Verify atomic write and safe read."""
    target = tmp_path / "test_file.txt"
    content = "Hello SSOT"
    
    # Write
    success = safe_write_file(target, content)
    assert success is True
    assert target.exists()
    
    # Read
    read_content = safe_read_file(target)
    assert read_content == content


def test_safe_write_creates_directories(tmp_path):
    """Verify safe_write_file creates parent directories."""
    target = tmp_path / "new" / "nested" / "dir" / "file.txt"
    content = "Nested content"
    
    # Parent directories don't exist yet
    assert not target.parent.exists()
    
    # Write should create them
    success = safe_write_file(target, content, make_dirs=True)
    assert success is True
    assert target.exists()
    assert safe_read_file(target) == content


def test_safe_read_nonexistent_file(tmp_path):
    """Verify safe_read_file returns None for nonexistent files."""
    nonexistent = tmp_path / "does_not_exist.txt"
    
    result = safe_read_file(nonexistent)
    assert result is None


def test_ensure_directory(tmp_path):
    """Verify directory creation."""
    target = tmp_path / "new" / "folder" / "structure"
    assert not target.exists()
    
    success = ensure_directory(target)
    assert success is True
    assert target.exists()
    assert target.is_dir()


def test_ensure_directory_existing(tmp_path):
    """Verify ensure_directory works on existing directories."""
    target = tmp_path / "existing"
    target.mkdir()
    
    # Should succeed without error
    success = ensure_directory(target)
    assert success is True
    assert target.exists()


def test_safe_delete_file(tmp_path):
    """Verify safe file deletion."""
    target = tmp_path / "to_delete.txt"
    target.write_text("delete me")
    
    assert target.exists()
    
    success = safe_delete_file(target)
    assert success is True
    assert not target.exists()


def test_safe_delete_nonexistent(tmp_path):
    """Verify safe_delete_file handles nonexistent files gracefully."""
    nonexistent = tmp_path / "does_not_exist.txt"
    
    # Should return True (no error) even if file doesn't exist
    success = safe_delete_file(nonexistent)
    assert success is True


def test_safe_copy_file(tmp_path):
    """Verify safe file copying."""
    src = tmp_path / "source.txt"
    dst = tmp_path / "destination.txt"
    content = "Copy this content"
    
    src.write_text(content)
    
    success = safe_copy_file(src, dst)
    assert success is True
    assert dst.exists()
    assert dst.read_text() == content
    # Source should still exist
    assert src.exists()


def test_safe_copy_creates_directories(tmp_path):
    """Verify safe_copy_file creates destination directories."""
    src = tmp_path / "source.txt"
    dst = tmp_path / "new" / "nested" / "destination.txt"
    content = "Copy to nested"
    
    src.write_text(content)
    
    success = safe_copy_file(src, dst, make_dirs=True)
    assert success is True
    assert dst.exists()
    assert dst.read_text() == content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

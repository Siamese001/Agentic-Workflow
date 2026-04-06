"""Foundational behavioral tests for agentic_core/utils/fs_util.py."""
from __future__ import annotations

from pathlib import Path


def test_module_importable():
    """Module fs_util must be importable."""
    from agentic_core.utils import fs_util
    assert fs_util is not None


def test_get_python_files_fast_happy_path():
    """get_python_files_fast must yield Python files from directory."""
    from agentic_core.utils import fs_util

    test_dir = Path(__file__).parent.parent.parent.parent.parent / "agentic_core" / "utils"
    files = list(fs_util.get_python_files_fast(test_dir, exclude_dirs=[]))
    assert len(files) > 0
    assert all(f.suffix == ".py" for f in files)


def test_get_python_files_fast_failure_path():
    """get_python_files_fast must handle non-existent directory gracefully."""
    from agentic_core.utils import fs_util

    non_existent = Path("/non/existent/path")
    files = list(fs_util.get_python_files_fast(non_existent, exclude_dirs=[]))
    assert len(files) == 0


def test_get_python_files_fast_edge_case():
    """get_python_files_fast must handle empty directory."""
    from agentic_core.utils import fs_util

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        files = list(fs_util.get_python_files_fast(Path(tmpdir), exclude_dirs=[]))
        assert len(files) == 0

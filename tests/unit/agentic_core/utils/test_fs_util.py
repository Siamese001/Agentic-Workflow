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
    import tempfile

    from agentic_core.utils import fs_util

    with tempfile.TemporaryDirectory() as tmpdir:
        files = list(fs_util.get_python_files_fast(Path(tmpdir), exclude_dirs=[]))
        assert len(files) == 0


def test_should_skip_scan_path_filters_junk_trees(tmp_path):
    """Shared scan helper must exclude cache, temp, and egg-info trees."""
    from agentic_core.utils.fs_util import should_skip_scan_path

    assert should_skip_scan_path(tmp_path / ".cache" / "x.py") is True
    assert should_skip_scan_path(tmp_path / "tmp_work" / "x.py") is True
    assert should_skip_scan_path(tmp_path / "_temp_build" / "x.py") is True
    assert should_skip_scan_path(tmp_path / "package.egg-info" / "x.py") is True
    assert should_skip_scan_path(Path("docs/archive/windsurf/legacy-tree/file.py")) is True
    assert should_skip_scan_path(Path("agentic_core/cache/cache_loader.py")) is False


def test_iter_scanned_files_prunes_junk_dirs(tmp_path):
    """Shared scanner walk helper must only yield real source files."""
    from agentic_core.utils.fs_util import iter_scanned_files

    good = tmp_path / "src" / "good.py"
    bad_cache = tmp_path / ".cache" / "bad.py"
    bad_tmp = tmp_path / "tmp_run" / "bad.py"
    good.parent.mkdir(parents=True)
    bad_cache.parent.mkdir(parents=True)
    bad_tmp.parent.mkdir(parents=True)
    good.write_text("print('ok')", encoding="utf-8")
    bad_cache.write_text("print('no')", encoding="utf-8")
    bad_tmp.write_text("print('no')", encoding="utf-8")

    files = list(iter_scanned_files(tmp_path, suffixes=(".py",), exclude_dirs=frozenset({".cache", "tmp_run"})))

    assert files == [good]

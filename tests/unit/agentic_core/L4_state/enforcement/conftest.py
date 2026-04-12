"""conftest for L4_state/enforcement tests - provides fixtures from conftest_isolation."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_memory_db(tmp_path, monkeypatch):
    """Redirect MEMORY_DB to a per-test temp SQLite so tests never touch
    the production artifacts/memory/knowledge_graph.sqlite."""
    test_db = tmp_path / "test_knowledge_graph.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(test_db))
    yield test_db


@pytest.fixture
def temp_directory():
    """Provide a temporary directory that gets cleaned up automatically."""
    temp_dir = Path(tempfile.mkdtemp(prefix="pytest_temp_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def isolated_cwd():
    """Provide an isolated current working directory."""
    original_cwd = Path.cwd()
    temp_dir = Path(tempfile.mkdtemp(prefix="pytest_cwd_"))
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def clean_env():
    """Provide a clean environment with minimal test variables."""
    original_env = os.environ.copy()

    # Keep essential variables but remove test additions
    essential_vars = [
        "PATH",
        "HOME",
        "USER",
        "TEMP",
        "TMP",
        "USERNAME",
        "COMPUTERNAME",
        "SYSTEMROOT",
        "WINDIR",
    ]

    clean_env = {k: v for k, v in original_env.items() if k in essential_vars}
    if "HOME" not in clean_env and "USERPROFILE" not in clean_env:
        fallback_home = original_env.get("USERPROFILE") or original_env.get("HOME") or str(Path.home())
        clean_env["USERPROFILE"] = fallback_home
    os.environ.clear()
    os.environ.update(clean_env)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

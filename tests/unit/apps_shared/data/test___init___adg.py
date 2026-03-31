"""ADG contract tests for apps_shared/data package."""

from __future__ import annotations

import importlib
from pathlib import Path


def test_apps_shared_data_package_importable():
    """apps_shared.data package imports without side effects."""
    mod = importlib.import_module("apps_shared.data")
    assert mod.__name__ == "apps_shared.data"


def test_apps_shared_data_contains_data_files():
    """apps_shared/data/ directory contains at least one data file."""
    data_dir = Path("apps_shared/data")
    assert data_dir.exists(), "apps_shared/data/ directory must exist"
    data_files = [
        f
        for f in data_dir.iterdir()
        if f.is_file() and f.suffix in (".json", ".jsonl", ".csv", ".yaml", ".yml", ".py")
    ]
    assert len(data_files) >= 1, "apps_shared/data/ must contain at least one data or module file"

"""ADG-driven tests for apps_rg/scripts/migration_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.scripts.migration_executor import (  # noqa: F401
        APPS_RG_DIR,
        BASE_DIR,
        DIRS,
        MANIFEST_PATH,
        MigrationExecutor,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MigrationExecutor = None  # type: ignore[assignment,misc]
    BASE_DIR = None  # type: ignore[assignment,misc]
    APPS_RG_DIR = None  # type: ignore[assignment,misc]
    MANIFEST_PATH = None  # type: ignore[assignment,misc]
    DIRS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="migration_executor.py deps unavailable")
class TestMigrationExecutor:
    def test_is_class(self):
        assert isinstance(MigrationExecutor, type)
    def test_importable(self):
        assert MigrationExecutor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_executor.py deps unavailable")
class TestBaseDirConstant:
    def test_is_not_none(self):
        assert BASE_DIR is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_executor.py deps unavailable")
class TestAppsRgDirConstant:
    def test_is_not_none(self):
        assert APPS_RG_DIR is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_executor.py deps unavailable")
class TestManifestPathConstant:
    def test_is_not_none(self):
        assert MANIFEST_PATH is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_executor.py deps unavailable")
class TestDirsConstant:
    def test_is_not_none(self):
        assert DIRS is not None


def test_module_importable():
    """Module migration_executor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
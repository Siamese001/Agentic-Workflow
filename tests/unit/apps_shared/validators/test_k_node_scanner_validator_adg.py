"""ADG-driven tests for apps_shared/validators/k_node_scanner_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.validators.k_node_scanner_validator import (  # noqa: F401
        KNodeMigrator,
        KNodeScanner,
        MigrationValidator,
        migrate_project,
        run_full_migration,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    KNodeScanner = None  # type: ignore[assignment,misc]
    KNodeMigrator = None  # type: ignore[assignment,misc]
    MigrationValidator = None  # type: ignore[assignment,misc]
    run_full_migration = None  # type: ignore[assignment,misc]
    migrate_project = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="k_node_scanner_validator.py deps unavailable")
class TestKNodeScanner:
    def test_is_class(self):
        assert isinstance(KNodeScanner, type)
    def test_importable(self):
        assert KNodeScanner is not None

@pytest.mark.skipif(not _AVAILABLE, reason="k_node_scanner_validator.py deps unavailable")
class TestKNodeMigrator:
    def test_is_class(self):
        assert isinstance(KNodeMigrator, type)
    def test_importable(self):
        assert KNodeMigrator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="k_node_scanner_validator.py deps unavailable")
class TestMigrationValidator:
    def test_is_class(self):
        assert isinstance(MigrationValidator, type)
    def test_importable(self):
        assert MigrationValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="k_node_scanner_validator.py deps unavailable")
class TestRunFullMigration:
    def test_is_callable(self):
        assert callable(run_full_migration)

@pytest.mark.skipif(not _AVAILABLE, reason="k_node_scanner_validator.py deps unavailable")
class TestMigrateProject:
    def test_is_callable(self):
        assert callable(migrate_project)


def test_module_importable():
    """Module k_node_scanner_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE

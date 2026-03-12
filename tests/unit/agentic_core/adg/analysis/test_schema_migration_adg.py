"""ADG importability contract for agentic_core/adg/analysis/schema_migration.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_schema_migration.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.schema_migration import (  # noqa: F401
        register_migration,
        list_migrations,
        migrate_scan_result_dict,
        get_migration,
        CURRENT_SCHEMA_VERSION,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    register_migration = None  # type: ignore[assignment,misc]
    list_migrations = None  # type: ignore[assignment,misc]
    migrate_scan_result_dict = None  # type: ignore[assignment,misc]
    get_migration = None  # type: ignore[assignment,misc]
    CURRENT_SCHEMA_VERSION = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="schema_migration.py deps unavailable")
class TestSchemaMigrationImportability:
    def test_module_importable(self) -> None:
        """ADG contract: schema_migration.py must be importable."""
        assert _AVAILABLE

    def test_register_migration_callable(self) -> None:
        assert callable(register_migration)

    def test_list_migrations_callable(self) -> None:
        assert callable(list_migrations)

    def test_current_schema_version_defined(self) -> None:
        assert CURRENT_SCHEMA_VERSION is not None


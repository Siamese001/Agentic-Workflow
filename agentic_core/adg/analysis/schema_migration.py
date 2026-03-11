"""E10: Schema Version Migration Guard.

Provides a registry of ADG schema version migrations.  When a
``ScanResult`` is loaded from a serialised snapshot that was produced by
an older scanner version, the appropriate migration callables are applied
in order to bring the data up to the current schema.

Migration registry format:
    {
        "from_version -> to_version": callable(data: dict) -> dict
    }

Each migration callable receives the raw dict (as produced by
``ScanResult.to_dict()``) and returns an updated dict.  Migrations are
applied in ascending lexicographic order of their ``from_version``.

Usage:
    from agentic_core.adg.analysis.schema_migration import migrate_scan_result_dict

    raw = json.loads(snapshot_file.read_text())
    migrated = migrate_scan_result_dict(raw)
    result = ScanResult.from_dict(migrated)
"""

from __future__ import annotations

import logging
from typing import Callable

logger = logging.getLogger(__name__)

MigrationFn = Callable[[dict], dict]

CURRENT_SCHEMA_VERSION = "1.0"

_MIGRATIONS: dict[tuple[str, str], MigrationFn] = {}


def register_migration(from_version: str, to_version: str) -> Callable[[MigrationFn], MigrationFn]:
    """Decorator that registers a migration callable.

    Example::

        @register_migration("0.9", "1.0")
        def migrate_0_9_to_1_0(data: dict) -> dict:
            for edge in data.get("edges", []):
                edge.setdefault("symbol", "")
            return data
    """

    def decorator(fn: MigrationFn) -> MigrationFn:
        _MIGRATIONS[(from_version, to_version)] = fn
        return fn

    return decorator


def list_migrations() -> list[tuple[str, str]]:
    """Return all registered migration pairs in lexicographic order."""
    return sorted(_MIGRATIONS.keys())


def migrate_scan_result_dict(data: dict) -> dict:
    """Apply all applicable migrations to a raw ScanResult dict.

    Detects the schema version from ``data["manifest"]["schema_version"]``
    (defaults to ``"0.9"`` for legacy data without the field).  Applies
    each migration in order until ``CURRENT_SCHEMA_VERSION`` is reached.

    Returns the migrated dict.  The original dict is NOT modified.
    """
    import copy

    data = copy.deepcopy(data)
    manifest = data.get("manifest", {})
    current = manifest.get("schema_version", "0.9")

    if current == CURRENT_SCHEMA_VERSION:
        return data

    sorted_pairs = sorted(_MIGRATIONS.keys())
    for from_v, to_v in sorted_pairs:
        if from_v == current:
            logger.debug("Migrating ADG schema %s -> %s", from_v, to_v)
            data = _MIGRATIONS[(from_v, to_v)](data)
            manifest = data.setdefault("manifest", {})
            manifest["schema_version"] = to_v
            current = to_v
            if current == CURRENT_SCHEMA_VERSION:
                break

    if current != CURRENT_SCHEMA_VERSION:
        logger.warning(
            "ADG schema migration incomplete: ended at %s, expected %s",
            current,
            CURRENT_SCHEMA_VERSION,
        )

    return data


def get_migration(from_version: str, to_version: str) -> MigrationFn | None:
    """Look up a specific registered migration, or None if not found."""
    return _MIGRATIONS.get((from_version, to_version))


# ---------------------------------------------------------------------------
# Built-in migrations
# ---------------------------------------------------------------------------


@register_migration("0.9", "1.0")
def _migrate_0_9_to_1_0(data: dict) -> dict:
    """0.9 -> 1.0: ensure every edge has a ``symbol`` field (was optional)."""
    for edge in data.get("edges", []):
        edge.setdefault("symbol", "")
    return data


__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "register_migration",
    "migrate_scan_result_dict",
    "get_migration",
    "list_migrations",
]

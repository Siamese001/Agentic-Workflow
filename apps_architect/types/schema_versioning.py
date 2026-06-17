"""Pattern schema versioning — backward-compatible migration support.

Plan: ``.claude/plans/apps-architect-deferred-scope-b8e3f1.md`` DW1 DS-3.

Patterns carry a schema_version field. When the schema evolves, migration
functions convert older patterns to the current version without breaking
existing collections.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from apps_architect.types.architect_types import Pattern

_log = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = "1.0"

MigrationFn = Callable[[dict[str, Any]], dict[str, Any]]

_MIGRATIONS: dict[str, MigrationFn] = {}


def register_migration(from_version: str, fn: MigrationFn) -> None:
    if from_version in _MIGRATIONS:
        _log.warning("Migration from %s already registered; overwriting", from_version)
    _MIGRATIONS[from_version] = fn


def migrate_pattern(pattern_dict: dict[str, Any]) -> dict[str, Any]:
    version = pattern_dict.get("schema_version", "1.0")
    result = dict(pattern_dict)
    while version != CURRENT_SCHEMA_VERSION:
        migrator = _MIGRATIONS.get(version)
        if migrator is None:
            _log.warning("No migration from schema %s; treating as current", version)
            result["schema_version"] = CURRENT_SCHEMA_VERSION
            break
        result = migrator(result)
        version = result.get("schema_version", CURRENT_SCHEMA_VERSION)
    return result


def pattern_to_dict(pattern: Pattern) -> dict[str, Any]:
    return {
        "pattern_id": pattern.pattern_id,
        "pattern_type": pattern.pattern_type.value,
        "source_ref": pattern.source_ref,
        "content_digest": pattern.content_digest,
        "first_seen": pattern.first_seen.isoformat(),
        "last_seen": pattern.last_seen.isoformat(),
        "schema_version": pattern.schema_version,
        "summary": pattern.summary,
        "tags": list(pattern.tags),
    }


def pattern_from_dict(data: dict[str, Any]) -> Pattern:
    from datetime import datetime

    migrated = migrate_pattern(data)
    return Pattern(
        pattern_id=migrated["pattern_id"],
        pattern_type=__import__("apps_architect.types").types.architect_types.PatternType(
            migrated["pattern_type"]
        ),
        source_ref=migrated["source_ref"],
        content_digest=migrated["content_digest"],
        first_seen=datetime.fromisoformat(migrated["first_seen"]),
        last_seen=datetime.fromisoformat(migrated["last_seen"]),
        schema_version=migrated.get("schema_version", "1.0"),
        summary=migrated.get("summary", ""),
        tags=tuple(migrated.get("tags", [])),
    )


__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "register_migration",
    "migrate_pattern",
    "pattern_to_dict",
    "pattern_from_dict",
]

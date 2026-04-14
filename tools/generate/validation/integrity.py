"""Artifact integrity checks for ADG generation."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from tqdm import tqdm


def _connect_sqlite(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(path), timeout=30)


def _check_artifact_validity(paths: object) -> None:
    """Verify all required artifacts exist and are valid.

    Fails with sys.exit(1) if any artifact is missing, zero-byte, or invalid.

    Args:
        paths: ArtifactPaths object containing file paths
    """
    required = {
        "snapshot": paths.snapshot,
        "sqlite": paths.sqlite,
    }

    missing = []
    zero_byte = []
    invalid = []

    for name, path in tqdm(required.items(), desc="Processing", unit="item"):
        if not path.exists():
            missing.append(name)
            continue

        if path.stat().st_size == 0:
            zero_byte.append(name)
            continue

        if name == "sqlite":
            try:
                conn = _connect_sqlite(path)
                conn.execute("SELECT 1 FROM nodes LIMIT 1")
                conn.close()
            except sqlite3.Error as e:
                invalid.append((name, str(e)))
        elif path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                invalid.append((name, str(e)))

    if missing or zero_byte or invalid:
        print("\n[ERROR] ADG artifact validation failed:")
        if missing:
            print(f"[ERROR] Missing artifacts: {', '.join(missing)}")
        if zero_byte:
            print(f"[ERROR] Zero-byte artifacts: {', '.join(zero_byte)}")
        if invalid:
            for name, err in invalid:
                print(f"[ERROR] Invalid {name}: {err}")
        print("[ERROR] Partial ADG generation detected - failing fast")
        sys.exit(1)


def _check_sqlite_integrity(sqlite_path: Path) -> None:
    """Verify SQLite database integrity and schema completeness.

    Fails with sys.exit(1) if integrity check fails or required tables are missing.

    Args:
        sqlite_path: Path to the SQLite database
    """
    try:
        conn = _connect_sqlite(sqlite_path)
        cur = conn.cursor()

        integrity_result = cur.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity_result != "ok":
            print(f"\n[ERROR] SQLite integrity check failed: {integrity_result}")
            conn.close()
            sys.exit(1)

        required_tables = {"nodes", "edges", "violations", "meta"}
        existing_tables = {
            row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

        missing_tables = required_tables - existing_tables
        if missing_tables:
            print(f"\n[ERROR] SQLite missing required tables: {', '.join(missing_tables)}")
            conn.close()
            sys.exit(1)

        conn.close()
    except sqlite3.Error as e:
        print(f"\n[ERROR] SQLite validation failed: {e}")
        sys.exit(1)


def _check_artifact_consistency(paths: object, artifact: object) -> None:
    """Verify artifact entity/relation counts match SQLite node/edge counts.

    Fails with sys.exit(1) if counts don't match. Skipped if JSON graphs not generated.

    Args:
        paths: ArtifactPaths object containing file paths
        artifact: ADGArtifact with entity and relation counts
    """
    if not hasattr(paths, "file_graph") or not paths.file_graph.exists():
        print("[ADG] Skipping artifact consistency check (JSON graphs disabled)")
        return

    conn = _connect_sqlite(paths.sqlite)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
    finally:
        conn.close()

    entity_count = len(artifact.entities) if hasattr(artifact, "entities") else 0
    relation_count = len(artifact.relations) if hasattr(artifact, "relations") else 0

    if entity_count != node_count or relation_count != edge_count:
        print("\n[ERROR] Artifact↔SQLite count mismatch:")
        print(f"[ERROR]   entities (JSON): {entity_count}")
        print(f"[ERROR]   nodes (SQLite): {node_count}")
        print(f"[ERROR]   relations (JSON): {relation_count}")
        print(f"[ERROR]   edges (SQLite): {edge_count}")
        print("[ERROR] Partial ADG generation detected - failing fast")
        sys.exit(1)

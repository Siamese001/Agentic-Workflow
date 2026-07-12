"""Contracts that keep one canonical ADG SQLite schema and writer authority."""

from __future__ import annotations

import importlib
import sqlite3

import pytest

from agentic_core.adg.artifact.sqlite_schema import DDL


def test_ddl_aliases_share_one_contract() -> None:
    artifact_paths = importlib.import_module(
        "agentic_core.adg.artifact.ArtifactPaths"
    )
    multi_writer = importlib.import_module(
        "agentic_core.adg.artifact.multi_writer"
    )

    assert artifact_paths._DDL is DDL
    assert multi_writer._DDL is DDL


def test_legacy_private_writer_delegates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    artifact_paths = importlib.import_module(
        "agentic_core.adg.artifact.ArtifactPaths"
    )
    multi_writer = importlib.import_module(
        "agentic_core.adg.artifact.multi_writer"
    )
    sentinel = tmp_path / "canonical.sqlite"
    marker = object()

    def fake_writer(graph, path):
        assert graph is marker
        assert path == sentinel
        return sentinel

    monkeypatch.setattr(artifact_paths, "_write_sqlite", fake_writer)
    assert multi_writer._write_sqlite(marker, sentinel) == sentinel


def test_canonical_ddl_shape_and_foreign_keys() -> None:
    with sqlite3.connect(":memory:") as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(DDL)

        edge_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(edges)")
        }
        assert "confidence_score" in edge_columns
        assert "confidence" not in edge_columns

        violation_columns = {
            row[1]: row[4]
            for row in conn.execute("PRAGMA table_info(violations)")
        }
        assert violation_columns["violation_class"] == "'hygiene'"

        edge_view_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(edge_view)")
        }
        assert "edge_confidence" in edge_view_columns

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO edges(
                    src_id, dst_id, relation_type, edge_kind,
                    source_file, line_no
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (10, 11, "imports", "static", "example.py", 1),
            )

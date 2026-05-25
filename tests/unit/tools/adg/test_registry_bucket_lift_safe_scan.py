"""Registry lift must install safe repo scan before consumer resolution."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.adg import registry_bucket_lift as lift_mod


def test_lift_installs_safe_scan_before_consumer_resolve(tmp_path: Path) -> None:
    db = tmp_path / "snap.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL DEFAULT 'registry_node',
            layer TEXT NOT NULL DEFAULT 'L_REGISTRY',
            identity_kind TEXT NOT NULL DEFAULT 'virtual',
            confidence TEXT NOT NULL DEFAULT 'HIGH',
            resolved_path TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL DEFAULT 'REGISTRY',
            source_file TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            symbol TEXT NOT NULL DEFAULT '',
            authority TEXT NOT NULL DEFAULT 'verified',
            bucket TEXT NOT NULL DEFAULT 'registry',
            resolution_status TEXT NOT NULL DEFAULT 'STABLE_REGISTRY',
            authority_status TEXT NOT NULL DEFAULT 'AUTHORITATIVE_REGISTRY',
            evidence_refs TEXT
        );
        """
    )
    con.close()

    installed: list[bool] = []

    def _fake_install() -> None:
        installed.append(True)

    with (
        patch.object(lift_mod, "_install_safe_repo_scan", side_effect=_fake_install),
        patch.object(lift_mod, "resolve_all_registries", return_value=[]),
        patch.object(lift_mod, "resolve_all_consumer_edges", return_value=[]),
    ):
        lift_mod.lift(static_snapshot=db, dry_run=True, include_consumer_edges=True)

    assert installed == [True]

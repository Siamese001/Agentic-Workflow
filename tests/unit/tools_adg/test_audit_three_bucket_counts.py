"""Regression tests for ``tools/adg/audit_three_bucket_counts.py`` (ADR-079 authority projection)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tools.adg.audit_three_bucket_counts import run_authority_audit


def _make_edges_snapshot(path: Path, authority_rows: list[tuple[str, int]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, authority TEXT)"
        )
        for auth, count in authority_rows:
            for _ in range(count):
                con.execute("INSERT INTO edges (authority) VALUES (?)", (auth,))
        con.commit()
    finally:
        con.close()
    return path


def test_run_authority_audit_projects_legacy_histogram(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(
        tmp_path / "snap.sqlite",
        [("verified", 3), ("unresolved", 2), ("runtime_observed", 1)],
    )
    result = run_authority_audit(snap)
    assert result["total_edges"] == 6
    assert result["before_legacy_authority_histogram"]["verified"] == 3
    assert result["after_projected_bucket_counts"]["static"] == 5
    assert result["after_projected_bucket_counts"]["runtime"] == 1
    assert result["proof_count"] >= 4


def test_run_authority_audit_writes_json_when_out_path_set(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(tmp_path / "snap.sqlite", [("verified", 1)])
    out = tmp_path / "counts.json"
    run_authority_audit(snap, out_path=out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["snapshot"] == snap.name
    assert payload["total_edges"] == 1


def test_run_authority_audit_ignores_unknown_legacy_authority(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(
        tmp_path / "snap.sqlite",
        [("verified", 1), ("<NULL>", 2), ("mystery_bucket", 4)],
    )
    result = run_authority_audit(snap)
    assert result["total_edges"] == 7
    assert result["after_projected_bucket_counts"]["static"] == 1

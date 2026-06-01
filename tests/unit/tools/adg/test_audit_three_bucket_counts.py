"""Unit tests for legacy authority → three-bucket projection (ADR-079 audit path)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.adg.audit_three_bucket_counts import run_authority_audit


def _make_edges_snapshot(path: Path, rows: list[tuple[str, int]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, authority TEXT)"
        )
        for authority, count in rows:
            for _ in range(count):
                con.execute("INSERT INTO edges (authority) VALUES (?)", (authority,))
        con.commit()
    finally:
        con.close()
    return path


def test_run_authority_audit_projects_legacy_histogram(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(
        tmp_path / "snap.sqlite",
        [
            ("verified", 10),
            ("unresolved", 3),
            ("runtime_observed", 2),
            ("external", 1),
        ],
    )
    result = run_authority_audit(snap)

    assert result["snapshot"] == "snap.sqlite"
    assert result["total_edges"] == 16
    assert result["after_projected_bucket_counts"]["static"] == 14
    assert result["after_projected_bucket_counts"]["runtime"] == 2
    assert result["proof_count"] == 12  # verified + runtime_observed authoritative
    assert result["risk_count"] == 3
    assert result["inventory_only_count"] == 1


def test_run_authority_audit_skips_null_and_unknown_legacy(tmp_path: Path) -> None:
    snap = tmp_path / "snap.sqlite"
    snap.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(snap))
    try:
        con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, authority TEXT)")
        con.executemany("INSERT INTO edges (authority) VALUES (?)", [("verified",)] * 2)
        con.execute("INSERT INTO edges (authority) VALUES (NULL)")
        con.executemany(
            "INSERT INTO edges (authority) VALUES (?)",
            [("legacy_unknown_bucket",)] * 4,
        )
        con.commit()
    finally:
        con.close()

    result = run_authority_audit(snap)

    assert result["total_edges"] == 7
    assert result["after_projected_bucket_counts"]["static"] == 2
    assert result["before_legacy_authority_histogram"]["<NULL>"] == 1
    assert result["before_legacy_authority_histogram"]["legacy_unknown_bucket"] == 4


def test_run_authority_audit_writes_json_when_out_path_set(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(tmp_path / "snap.sqlite", [("verified", 1)])
    out = tmp_path / "audit.json"
    run_authority_audit(snap, out_path=out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_edges"] == 1
    assert payload["proof_count"] == 1


def test_run_authority_audit_empty_edges_zero_totals(tmp_path: Path) -> None:
    snap = _make_edges_snapshot(tmp_path / "empty.sqlite", [])
    result = run_authority_audit(snap)

    assert result["total_edges"] == 0
    assert result["proof_count"] == 0
    assert result["risk_count"] == 0

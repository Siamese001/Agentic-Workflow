"""Unit tests: legacy authority histogram → three-bucket projection (ADR-079 audit path)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tools.adg.audit_three_bucket_counts import run_authority_audit


def _mini_snapshot(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE edges (authority TEXT)")
        rows = [
            ("verified",),
            ("verified",),
            ("runtime_observed",),
            ("unresolved",),
            (None,),
            ("unknown_legacy",),
        ]
        con.executemany("INSERT INTO edges (authority) VALUES (?)", rows)
        con.commit()
    finally:
        con.close()


def test_run_authority_audit_projects_buckets_and_proof_counts(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_test.sqlite"
    _mini_snapshot(snap)

    result = run_authority_audit(snap)

    assert result["snapshot"] == "adg_indexed_test.sqlite"
    assert result["total_edges"] == 6
    assert result["before_legacy_authority_histogram"]["verified"] == 2
    assert result["after_projected_bucket_counts"] == {
        "static": 3,
        "runtime": 1,
        "registry": 0,
    }
    assert result["proof_count"] == 3
    assert result["risk_count"] == 1
    assert result["inventory_only_count"] == 0


def test_run_authority_audit_writes_json_when_out_path_set(tmp_path: Path) -> None:
    snap = tmp_path / "snap.sqlite"
    _mini_snapshot(snap)
    out = tmp_path / "authority_counts.json"

    run_authority_audit(snap, out_path=out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_edges"] == 6
    assert out.read_text(encoding="utf-8").endswith("\n")


def test_run_authority_audit_empty_snapshot(tmp_path: Path) -> None:
    snap = tmp_path / "empty.sqlite"
    con = sqlite3.connect(snap)
    try:
        con.execute("CREATE TABLE edges (authority TEXT)")
        con.commit()
    finally:
        con.close()

    result = run_authority_audit(snap)
    assert result["total_edges"] == 0
    assert result["proof_count"] == 0
    assert result["after_projected_bucket_counts"] == {"static": 0, "runtime": 0, "registry": 0}

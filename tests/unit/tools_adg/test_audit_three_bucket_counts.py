"""Unit tests: legacy ADG edge authority → three-bucket projection (ADR-079)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.adg.audit_three_bucket_counts import run_authority_audit


def _snapshot_with_authorities(path: Path, rows: list[tuple[str | None, int]]) -> Path:
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
                con.execute("INSERT INTO edges(authority) VALUES (?)", (authority,))
        con.commit()
    finally:
        con.close()
    return path


def test_run_authority_audit_projects_legacy_histogram(tmp_path: Path) -> None:
    snap = _snapshot_with_authorities(
        tmp_path / "adg_indexed_test.sqlite",
        [
            ("verified", 3),
            ("unresolved", 2),
            ("runtime_observed", 1),
            ("external", 1),
            (None, 1),
            ("legacy_unknown", 1),
        ],
    )
    result = run_authority_audit(snap)

    assert result["snapshot"] == snap.name
    assert result["total_edges"] == 9
    assert result["before_legacy_authority_histogram"]["verified"] == 3
    assert result["after_projected_bucket_counts"] == {"static": 7, "runtime": 1, "registry": 0}
    assert result["proof_count"] == 4  # 3 AUTHORITATIVE + 1 AUTHORITATIVE_RUNTIME
    assert result["risk_count"] == 2  # unresolved → RISK_SIGNAL_ONLY
    assert result["inventory_only_count"] == 1  # external → EXTERNAL_ONLY


def test_run_authority_audit_writes_json_when_out_path_set(tmp_path: Path) -> None:
    snap = _snapshot_with_authorities(
        tmp_path / "adg_indexed_write.sqlite",
        [("verified", 1)],
    )
    out = tmp_path / "authority_counts.json"
    result = run_authority_audit(snap, out_path=out)

    assert out.is_file()
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk["proof_count"] == result["proof_count"] == 1


def test_run_authority_audit_empty_snapshot_zero_counts(tmp_path: Path) -> None:
    snap = _snapshot_with_authorities(tmp_path / "adg_indexed_empty.sqlite", [])
    result = run_authority_audit(snap)

    assert result["total_edges"] == 0
    assert result["proof_count"] == 0
    assert result["risk_count"] == 0
    assert result["inventory_only_count"] == 0

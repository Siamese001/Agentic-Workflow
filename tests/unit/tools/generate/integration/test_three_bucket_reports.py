"""Unit tests for optional three-bucket report emission (gap + authority audit)."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
_REPORTS_PATH = _REPO_ROOT / "tools" / "generate" / "integration" / "three_bucket_reports.py"
_spec = importlib.util.spec_from_file_location("three_bucket_reports", _REPORTS_PATH)
assert _spec and _spec.loader
_reports_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reports_mod)
emit_three_bucket_reports = _reports_mod.emit_three_bucket_reports


def _minimal_snapshot(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE nodes (id INTEGER PRIMARY KEY, resolved_path TEXT, "
            "file_path TEXT, adg_name TEXT)"
        )
        con.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INT, dst_id INT, "
            "relation_type TEXT, authority TEXT)"
        )
        con.execute("INSERT INTO edges (authority) VALUES ('verified')")
        con.commit()
    finally:
        con.close()
    return path


def test_emit_three_bucket_reports_writes_gap_and_audit_artifacts(tmp_path: Path) -> None:
    snap = _minimal_snapshot(tmp_path / "snap.sqlite")
    out_dir = tmp_path / "reports"

    paths = emit_three_bucket_reports(snap, out_dir=out_dir)

    gap_json = paths["gap_json"]
    gap_md = paths["gap_md"]
    audit_json = paths["authority_audit"]

    assert gap_json.is_file()
    assert gap_md.is_file()
    assert audit_json.is_file()

    gap_payload = json.loads(gap_json.read_text(encoding="utf-8"))
    assert "health_score_pct_triplet_attested" in gap_payload
    assert gap_md.read_text(encoding="utf-8").strip()

    audit_payload = json.loads(audit_json.read_text(encoding="utf-8"))
    assert audit_payload["total_edges"] == 1
    assert audit_payload["proof_count"] == 1

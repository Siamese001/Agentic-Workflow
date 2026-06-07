"""Tests for W3 hardening of ``tools/adg/three_bucket_gap_report.py``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-audit-pipeline-integration-7f2c93.md`` W4.2.

Covers:
- runtime_proof_status field emission (json + md)
- --require-runtime-proof exit behavior
- runtime-thin banner in markdown
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from tools.adg import three_bucket_gap_report as report_mod

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tools" / "adg" / "three_bucket_gap_report.py"


def _make_snapshot(path: Path, *, with_runtime_view: bool, attested: int) -> Path:
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
        if with_runtime_view:
            con.execute(
                "CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)"
            )
            for _ in range(attested):
                con.execute(
                    "INSERT INTO v_runtime_proof(static_edge_id, attesting_trace_count) VALUES (NULL, 1)"
                )
        con.commit()
    finally:
        con.close()
    return path


# ---------------------------------------------------------------------------
# 19. test_report_does_not_treat_static_only_as_runtime_proof
# ---------------------------------------------------------------------------
def test_report_does_not_treat_static_only_as_runtime_proof(tmp_path):
    snap = _make_snapshot(tmp_path / "snap.sqlite", with_runtime_view=False, attested=0)
    r = report_mod.run_report(snap, top_n=5)
    assert r["runtime_view_present"] is False
    assert r["runtime_attested_edges"] == 0
    assert r["runtime_proof_status"] == "view_absent"


# ---------------------------------------------------------------------------
# 20. test_report_does_not_treat_synthetic_evidence_as_runtime_proof
# ---------------------------------------------------------------------------
def test_report_does_not_treat_synthetic_evidence_as_runtime_proof(tmp_path):
    # View present, zero attested rows (attesting_trace_count < 1).
    snap = tmp_path / "snap.sqlite"
    con = sqlite3.connect(str(snap))
    try:
        con.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, resolved_path TEXT, file_path TEXT, adg_name TEXT)")
        con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INT, dst_id INT, relation_type TEXT, authority TEXT)")
        con.execute("CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)")
        con.execute("INSERT INTO v_runtime_proof VALUES (NULL, 0)")  # synthetic/unattested
        con.commit()
    finally:
        con.close()
    r = report_mod.run_report(snap, top_n=5)
    assert r["runtime_proof_status"] == "view_present_zero_attested"


# ---------------------------------------------------------------------------
# 21. test_require_runtime_proof_fails_when_view_missing
# ---------------------------------------------------------------------------
def test_require_runtime_proof_fails_when_view_missing(tmp_path):
    snap = _make_snapshot(tmp_path / "snap.sqlite", with_runtime_view=False, attested=0)
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT),
         "--snapshot", str(snap),
         "--out-dir", str(tmp_path / "out"),
         "--format", "json",
         "--require-runtime-proof"],
        cwd=str(REPO_ROOT), timeout=60, shell=False, check=False,
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "require-runtime-proof" in (proc.stderr or "") or "runtime_proof_status" in (proc.stderr or "")


# ---------------------------------------------------------------------------
# 22. test_require_runtime_proof_fails_when_zero_attested
# ---------------------------------------------------------------------------
def test_require_runtime_proof_fails_when_zero_attested(tmp_path):
    snap = tmp_path / "snap.sqlite"
    con = sqlite3.connect(str(snap))
    try:
        con.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, resolved_path TEXT, file_path TEXT, adg_name TEXT)")
        con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INT, dst_id INT, relation_type TEXT, authority TEXT)")
        con.execute("CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)")
        con.execute("INSERT INTO v_runtime_proof VALUES (NULL, 0)")
        con.commit()
    finally:
        con.close()
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT),
         "--snapshot", str(snap),
         "--out-dir", str(tmp_path / "out"),
         "--format", "json",
         "--require-runtime-proof"],
        cwd=str(REPO_ROOT), timeout=60, shell=False, check=False,
        capture_output=True, text=True,
    )
    assert proc.returncode == 2


# ---------------------------------------------------------------------------
# 23. test_runtime_proof_status_field_present_in_json_and_md
# ---------------------------------------------------------------------------
def test_runtime_proof_status_field_present_in_json_and_md(tmp_path):
    snap = _make_snapshot(tmp_path / "snap.sqlite", with_runtime_view=True, attested=3)
    out_dir = tmp_path / "out"
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT),
         "--snapshot", str(snap),
         "--out-dir", str(out_dir),
         "--format", "both"],
        cwd=str(REPO_ROOT), timeout=60, shell=False, check=False,
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads((out_dir / "THREE_BUCKET_GAP_REPORT.json").read_text())
    assert data["runtime_proof_status"] == "attested"
    md = (out_dir / "THREE_BUCKET_GAP_REPORT.md").read_text()
    assert "Runtime proof status" in md
    assert "`attested`" in md
    # Banner should NOT be present when attested.
    assert "DIAGNOSTIC ONLY — RUNTIME-THIN" not in md


def test_report_includes_snapshot_fingerprint_fields(tmp_path):
    snap = _make_snapshot(tmp_path / "snap.sqlite", with_runtime_view=True, attested=2)
    r = report_mod.run_report(snap, top_n=5)
    assert r.get("source_snapshot_sha256")
    assert len(str(r["source_snapshot_sha256"])) == 64
    assert r.get("source_snapshot_mtime_iso")
    assert r["snapshot"] == snap.name


def test_runtime_thin_banner_shown_when_not_attested(tmp_path):
    snap = _make_snapshot(tmp_path / "snap.sqlite", with_runtime_view=False, attested=0)
    out_dir = tmp_path / "out"
    subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT),
         "--snapshot", str(snap),
         "--out-dir", str(out_dir),
         "--format", "md"],
        cwd=str(REPO_ROOT), timeout=60, shell=False, check=False,
        capture_output=True, text=True,
    )
    md = (out_dir / "THREE_BUCKET_GAP_REPORT.md").read_text()
    assert "DIAGNOSTIC ONLY" in md
    assert "RUNTIME-THIN" in md

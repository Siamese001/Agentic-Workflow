"""Tests for ops_scripts/ci/check_runtime_proof_view_well_formed.py.

Tier: unit
Plan: docs/archive/windsurf/legacy-tree/plans/three-bucket-otel-view-5db409.md (W4.P4.1)
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_runtime_proof_view_well_formed.py"

__adg_consumer_mode__ = "inventory"


def _make_snapshot_with_v_runtime_proof(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.executescript(
        """
        CREATE TABLE v_runtime_proof (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            src_name              TEXT NOT NULL,
            dst_name              TEXT NOT NULL,
            relation_type         TEXT NOT NULL,
            edge_kind             TEXT NOT NULL DEFAULT 'RUNTIME_OBSERVED',
            static_edge_id        INTEGER,
            attesting_trace_count INTEGER NOT NULL DEFAULT 0,
            latest_trace_id       TEXT DEFAULT '',
            latest_span_id        TEXT DEFAULT '',
            last_seen_at          TEXT DEFAULT '',
            evidence_refs         TEXT,
            bucket                TEXT NOT NULL DEFAULT 'runtime',
            resolution_status     TEXT NOT NULL DEFAULT 'VERIFIED_RUNTIME',
            authority_status      TEXT NOT NULL DEFAULT 'AUTHORITATIVE_RUNTIME',
            UNIQUE(src_name, dst_name, relation_type)
        );
        """
    )
    return con


def _run_gate(snapshot: Path, *, strict: bool = False, env: dict | None = None) -> tuple[int, str]:
    cmd = [sys.executable, str(GATE), "--snapshot", str(snapshot)]
    if strict:
        cmd.append("--strict")
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        env=full_env,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestGateMissingSnapshot:
    def test_missing_snapshot_skips_gracefully(self, tmp_path: Path) -> None:
        bad = tmp_path / "missing.sqlite"
        rc, out = _run_gate(bad)
        assert rc == 0  # advisory: skip on missing
        assert "no static ADG snapshot found" in out or "table missing" in out or "missing" in out.lower()


class TestGateMissingTable:
    def test_missing_table_skip(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        # Create a sqlite file without v_runtime_proof.
        sqlite3.connect(str(snap)).close()
        rc, out = _run_gate(snap)
        assert rc == 0
        assert "v_runtime_proof table missing" in out


class TestGateEmptyTable:
    def test_empty_table_passes(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.commit()
        con.close()
        rc, out = _run_gate(snap)
        assert rc == 0
        assert "rows=0" in out
        assert "violations=0" in out


class TestGateValidRows:
    def test_valid_rows_pass(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 1, 'trace_x', 'AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
        con.close()
        rc, out = _run_gate(snap)
        assert rc == 0
        assert "rows=1" in out
        assert "violations=0" in out


class TestGateMissingTraceId:
    def test_authoritative_without_trace_id_violates(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        # AUTHORITATIVE_RUNTIME but empty trace_id — fabricated evidence.
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 1, '', 'AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
        con.close()
        # Advisory mode: violation reported but exit 0.
        rc, out = _run_gate(snap, strict=False)
        assert rc == 0
        assert "missing_trace_id" in out

    def test_strict_mode_blocks_on_violation(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 1, '', 'AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
        con.close()
        rc, out = _run_gate(snap, strict=True)
        assert rc == 1
        assert "missing_trace_id" in out


class TestGateInvalidAuthority:
    def test_unknown_authority_status_flagged(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 1, 'tx', 'WEIRD_VALUE')"
        )
        con.commit()
        con.close()
        rc, out = _run_gate(snap)
        assert rc == 0
        assert "invalid_authority_status" in out


class TestGateZeroAttesting:
    def test_authoritative_with_zero_attesting_count_flagged(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 0, 'tx', 'AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
        con.close()
        rc, out = _run_gate(snap)
        assert rc == 0
        assert "zero_attesting_count" in out


class TestGateBypass:
    def test_bypass_envvar_skips_all_checks(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        # Insert a guaranteed violation.
        con.execute(
            "INSERT INTO v_runtime_proof(src_name, dst_name, relation_type, "
            "attesting_trace_count, latest_trace_id, authority_status) "
            "VALUES ('a', 'b', 'parent_child', 1, '', 'AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
        con.close()
        rc, out = _run_gate(snap, strict=True, env={"RUNTIME_PROOF_VIEW_BYPASS": "1"})
        assert rc == 0
        assert "bypass active" in out


class TestGateReport:
    def test_report_written_to_disk(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_snapshot_with_v_runtime_proof(snap)
        con.commit()
        con.close()
        _run_gate(snap)
        report = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "adg"
            / "runtime_proof_view_gate_report.json"
        )
        assert report.exists()
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["gate"] == "G-RUNTIME-PROOF-VIEW-WELL-FORMED"

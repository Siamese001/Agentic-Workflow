"""Unit tests for tools/adg/remediate_three_graph_defects.py.

Each test seeds a tiny synthetic snapshot with one specific defect,
applies the remediation, and asserts the defect is gone — providing
before/after evidence for the three remediated categories.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
TOOL = REPO_ROOT / "tools" / "adg" / "remediate_three_graph_defects.py"


def _make_minimal_snapshot(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, entity_type TEXT, layer TEXT);
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER, dst_id INTEGER, relation_type TEXT, edge_kind TEXT,
            source_file TEXT, line_no INTEGER, symbol TEXT,
            dynamic_resolution TEXT, authority TEXT, bucket TEXT,
            resolution_status TEXT, authority_status TEXT, evidence_refs TEXT
        );
        """
    )
    con.execute("INSERT INTO meta(key,value) VALUES('artifact_digest','d1g3st0000')")
    con.execute("INSERT INTO meta(key,value) VALUES('schema_version','4.0.0')")
    con.commit()
    con.close()


def _run_tool(snap: Path, *, dry_run: bool = False, skip_projection: bool = True) -> dict:
    """Invoke the remediation tool and return the parsed JSON report."""
    json_out = snap.parent / "report.json"
    args = [
        sys.executable, str(TOOL),
        "--snapshot", str(snap),
        "--json-out", str(json_out),
    ]
    if dry_run:
        args.append("--dry-run")
    if skip_projection:
        args.append("--skip-projection")
    proc = subprocess.run(
        args, cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert json_out.exists(), f"no report; stdout={proc.stdout}\nstderr={proc.stderr}"
    return json.loads(json_out.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# D2 — authority enum migration
# ---------------------------------------------------------------------------


class TestD2AuthorityMigration:
    def test_static_canonical_migrates_to_verified(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        # 5 rows out-of-enum
        for i in range(5):
            con.execute(
                "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
                "resolution_status,authority_status) "
                "VALUES (1,2,'imports','static_canonical','static','V','A')"
            )
        con.commit()
        con.close()

        report = _run_tool(snap, skip_projection=True)
        d2 = report["d2_authority_enum"]
        assert d2["before_distribution"].get("static_canonical") == 5
        assert d2["migrations_applied"] == {
            "static_canonical->verified": 5,
            "registry_declared->verified": 0,
        }
        assert d2["after_distribution"].get("verified") == 5
        assert d2["out_of_enum_after"] == {}
        assert d2["fix_applied"] is True

    def test_registry_declared_migrates_to_verified(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        for i in range(7):
            con.execute(
                "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
                "resolution_status,authority_status) "
                "VALUES (1,2,'MCP_SERVER_DECLARED','registry_declared','registry','S','AR')"
            )
        con.commit()
        con.close()

        report = _run_tool(snap, skip_projection=True)
        d2 = report["d2_authority_enum"]
        assert d2["before_distribution"].get("registry_declared") == 7
        assert d2["migrations_applied"]["registry_declared->verified"] == 7
        assert d2["out_of_enum_after"] == {}
        assert d2["fix_applied"] is True

    def test_does_not_mass_fill_null_authority(self, tmp_path):
        """Per user constraint: NULL rows must not be auto-classified as verified."""
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        # Real out-of-enum row (will be migrated)
        con.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
            "resolution_status,authority_status) "
            "VALUES (1,2,'imports','static_canonical','static','V','A')"
        )
        # NULL-authority rows — must remain NULL after the run.
        for _ in range(3):
            con.execute(
                "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
                "resolution_status,authority_status) "
                "VALUES (1,2,'imports',NULL,'static','V','A')"
            )
        con.commit()
        con.close()

        report = _run_tool(snap, skip_projection=True)
        d2 = report["d2_authority_enum"]
        assert d2["null_authority_before"] == 3
        assert d2["null_authority_after"] == 3, (
            "remediation must not mass-fill NULL authority rows"
        )

    def test_dry_run_does_not_modify(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        con.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
            "resolution_status,authority_status) "
            "VALUES (1,2,'imports','static_canonical','static','V','A')"
        )
        con.commit()
        con.close()

        report = _run_tool(snap, dry_run=True, skip_projection=True)
        d2 = report["d2_authority_enum"]
        assert d2["fix_applied"] is False
        # Row still present with old label.
        con = sqlite3.connect(snap)
        n = con.execute(
            "SELECT COUNT(*) FROM edges WHERE authority='static_canonical'"
        ).fetchone()[0]
        con.close()
        assert n == 1


# ---------------------------------------------------------------------------
# D3 — I3 violation_propagates_through dynamic_resolution
# ---------------------------------------------------------------------------


class TestD3I3Propagation:
    def test_propagation_edges_get_derived_resolution(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        for i in range(11):
            con.execute(
                "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,"
                "source_file,authority,bucket,resolution_status,authority_status,"
                "dynamic_resolution) "
                "VALUES (1,2,'violation_propagates_through','violation_propagation',"
                "NULL,'verified','static','V','A','')"
            )
        con.commit()
        con.close()

        report = _run_tool(snap, skip_projection=True)
        d3 = report["d3_impossible_states_i3"]
        assert d3["before_violators"] == 11
        assert d3["rows_updated"] == 11
        assert d3["after_violators"] == 0
        assert d3["fix_applied"] is True

    def test_does_not_touch_non_propagation_rows(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        # Propagation row — should be updated.
        con.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,"
            "authority,bucket,resolution_status,authority_status,dynamic_resolution)"
            " VALUES (1,2,'violation_propagates_through','violation_propagation',"
            "NULL,'verified','static','V','A','')"
        )
        # Unrelated row — should NOT be updated.
        con.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,"
            "authority,bucket,resolution_status,authority_status,dynamic_resolution)"
            " VALUES (1,2,'imports','static_call','foo.py','verified','static','V','A','')"
        )
        con.commit()
        con.close()

        _run_tool(snap, skip_projection=True)
        con = sqlite3.connect(snap)
        # The imports row stays untouched.
        unrelated = con.execute(
            "SELECT dynamic_resolution FROM edges WHERE relation_type='imports'"
        ).fetchone()[0]
        # The propagation row gets 'derived'.
        propagation = con.execute(
            "SELECT dynamic_resolution FROM edges WHERE relation_type='violation_propagates_through'"
        ).fetchone()[0]
        con.close()
        assert unrelated == ""
        assert propagation == "derived"


class TestIdempotency:
    def test_double_apply_is_safe(self, tmp_path):
        snap = tmp_path / "snap.sqlite"
        _make_minimal_snapshot(snap)
        con = sqlite3.connect(snap)
        con.execute(
            "INSERT INTO edges(src_id,dst_id,relation_type,authority,bucket,"
            "resolution_status,authority_status) "
            "VALUES (1,2,'MCP_SERVER_DECLARED','registry_declared','registry','S','AR')"
        )
        con.commit()
        con.close()

        first = _run_tool(snap, skip_projection=True)
        assert first["d2_authority_enum"]["fix_applied"] is True

        second = _run_tool(snap, skip_projection=True)
        d2_2 = second["d2_authority_enum"]
        # Second run finds no out-of-enum rows; no migrations applied.
        assert d2_2["out_of_enum_before"] == {}
        assert d2_2["fix_applied"] is False
        assert d2_2["null_authority_after"] == 0

"""Schema-guard regression tests for two CI gates.

Plan: NEXT_STEP `adg-ci-script-schema-fixes`. Both
``check_exception_contract.py`` (queries `edges.symbol`) and
``check_test_harness_coverage.py`` (queries the `nodes` table) used to
crash with ``sqlite3.OperationalError`` when handed a stub/sentinel
snapshot or an in-flight pipeline snapshot. The fixes added a schema
guard at the top of each gate's main() that emits a SKIP and exits 0
instead.

These tests construct a stub sqlite missing the required columns/tables,
invoke each gate, and assert exit 0 + SKIP message.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]


def _make_stub_sqlite(path: Path, *, with_nodes: bool, with_edge_symbol: bool) -> None:
    """Build a stub ADG sqlite missing schema parts the gates rely on."""
    con = sqlite3.connect(path)
    cur = con.cursor()
    if with_edge_symbol:
        cur.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, relation_type TEXT, "
            "source_file TEXT, line_no INTEGER, symbol TEXT)"
        )
    else:
        cur.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, relation_type TEXT, "
            "source_file TEXT, line_no INTEGER)"
        )
    if with_nodes:
        cur.execute(
            "CREATE TABLE nodes (id TEXT PRIMARY KEY, adg_name TEXT, "
            "entity_type TEXT, resolved_path TEXT)"
        )
    con.commit()
    con.close()


def _run_gate(script: Path, sqlite: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--sqlite", str(sqlite)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


class TestExceptionContractSchemaGuard:
    def test_skip_when_edges_lacks_symbol_column(self, tmp_path: Path) -> None:
        stub = tmp_path / "adg_indexed_stub.sqlite"
        _make_stub_sqlite(stub, with_nodes=False, with_edge_symbol=False)
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_exception_contract.py",
            stub,
        )
        assert result.returncode == 0, (
            f"expected SKIP exit 0, got {result.returncode}\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "SKIP" in result.stdout
        assert "symbol" in result.stdout
        # Must NOT contain a Python traceback
        assert "Traceback" not in result.stderr
        assert "OperationalError" not in (result.stdout + result.stderr)

    def test_skip_when_edges_table_missing(self, tmp_path: Path) -> None:
        # Build sqlite with no `edges` table at all
        stub = tmp_path / "adg_indexed_stub.sqlite"
        con = sqlite3.connect(stub)
        con.execute("CREATE TABLE bogus (x INTEGER)")
        con.commit()
        con.close()
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_exception_contract.py",
            stub,
        )
        # The pragma returns no rows on missing table — branch falls through to
        # the empty-cols SKIP message. Either route is acceptable as long as
        # the script does not crash.
        assert result.returncode == 0, (
            f"got {result.returncode}: {result.stdout} | {result.stderr}"
        )
        assert "SKIP" in result.stdout

    def test_runs_when_symbol_column_present(self, tmp_path: Path) -> None:
        # Smoke check: with the column present the script does not SKIP on
        # schema; it proceeds (and may legitimately PASS or fail later).
        stub = tmp_path / "adg_indexed_stub.sqlite"
        _make_stub_sqlite(stub, with_nodes=True, with_edge_symbol=True)
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_exception_contract.py",
            stub,
        )
        assert "SKIP: snapshot `edges` table has no `symbol` column" not in result.stdout


class TestTestHarnessCoverageSchemaGuard:
    def test_skip_when_nodes_table_missing(self, tmp_path: Path) -> None:
        stub = tmp_path / "adg_indexed_stub.sqlite"
        _make_stub_sqlite(stub, with_nodes=False, with_edge_symbol=True)
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_test_harness_coverage.py",
            stub,
        )
        assert result.returncode == 0, (
            f"expected SKIP exit 0, got {result.returncode}\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "SKIP" in result.stdout
        assert "nodes" in result.stdout
        assert "Traceback" not in result.stderr
        assert "OperationalError" not in (result.stdout + result.stderr)

    def test_no_skip_when_nodes_table_present(self, tmp_path: Path) -> None:
        stub = tmp_path / "adg_indexed_stub.sqlite"
        _make_stub_sqlite(stub, with_nodes=True, with_edge_symbol=True)
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_test_harness_coverage.py",
            stub,
        )
        assert "SKIP: snapshot lacks `nodes` table" not in result.stdout


class TestSentinelSnapshotSafety:
    """Both gates must tolerate the canonical sentinel snapshot at
    `artifacts/adg/adg_indexed_99999999_9999.sqlite` without crashing.
    """

    def test_exception_contract_against_sentinel(self) -> None:
        sentinel = REPO / "artifacts" / "adg" / "adg_indexed_99999999_9999.sqlite"
        if not sentinel.is_file():
            pytest.skip("sentinel snapshot not present")
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_exception_contract.py",
            sentinel,
        )
        assert result.returncode == 0
        assert "SKIP" in result.stdout

    def test_test_harness_coverage_against_sentinel(self) -> None:
        sentinel = REPO / "artifacts" / "adg" / "adg_indexed_99999999_9999.sqlite"
        if not sentinel.is_file():
            pytest.skip("sentinel snapshot not present")
        result = _run_gate(
            REPO / "ops_scripts" / "ci" / "check_test_harness_coverage.py",
            sentinel,
        )
        assert result.returncode == 0
        assert "SKIP" in result.stdout

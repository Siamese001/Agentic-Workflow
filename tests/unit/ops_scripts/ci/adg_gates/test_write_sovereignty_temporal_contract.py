"""Fail-closed tests for P0 write-sovereignty temporal evidence."""

from __future__ import annotations

import sqlite3

from ops_scripts.ci.adg_gates.gate_p0_write_sovereignty import (
    WriteSovereigntyGate,
)


def _database(path, *, include_delta: bool, comparison_status: str = "EXACT"):
    with sqlite3.connect(path) as conn:
        conn.execute(
            """CREATE TABLE mv_write_sovereignty_paths (
                edge_id INTEGER,
                writer_file TEXT,
                writer_layer TEXT,
                write_symbol TEXT,
                write_line INTEGER,
                source_file TEXT,
                is_uwg_routed INTEGER,
                is_direct_infra_write INTEGER,
                severity TEXT
            )"""
        )
        if include_delta:
            conn.execute(
                """CREATE TABLE mv_new_write_bypass_paths (
                    edge_id INTEGER,
                    src_file TEXT,
                    src_layer TEXT,
                    bypass_type TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    is_new INTEGER,
                    comparison_status TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO mv_new_write_bypass_paths VALUES "
                "(1, 'a.py', 'L2', 'sqlite', 'a.py', 1, NULL, ?)",
                (comparison_status,),
            )
    return path


def _evaluate(path):
    gate = WriteSovereigntyGate(sqlite_path=path)
    gate._connect()
    try:
        return gate._execute_gate_logic()
    finally:
        if gate.conn is not None:
            gate.conn.close()


def test_no_baseline_blocks_p0_gate(tmp_path):
    result = _evaluate(
        _database(
            tmp_path / "no_baseline.sqlite",
            include_delta=True,
            comparison_status="NO_BASELINE",
        )
    )

    assert result.status == "blocked"
    assert result.summary["baseline_status"] == "NO_BASELINE"
    assert any(
        violation.violation_id == "write_delta_baseline_unavailable"
        for violation in result.violations
    )


def test_missing_delta_table_blocks_p0_gate(tmp_path):
    result = _evaluate(
        _database(
            tmp_path / "missing_delta.sqlite",
            include_delta=False,
        )
    )

    assert result.status == "blocked"
    assert result.summary["baseline_status"] == "UNAVAILABLE"
    assert any(
        violation.violation_id == "write_delta_evaluation_unavailable"
        for violation in result.violations
    )

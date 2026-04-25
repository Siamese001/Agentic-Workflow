"""Unit tests for ``agentic_core.L6_observability.decision_events_schema``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W1.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid

import pytest

from agentic_core.L6_observability.decision_events_schema import (
    DECISION_LAYERS,
    DecisionEventRow,
    UnknownDecisionLayerError,
    ensure_schema,
    insert_decision_event,
    migrate_from_routing_decision_events,
)


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


def _row(**overrides) -> DecisionEventRow:
    base = {
        "decision_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "decision_layer": "L0_routing",
        "app_name": "test_app",
        "request_hash": "abc123",
        "chosen_route": "R1A",
        "policy_hash": "policy_v1",
        "snapshot_id": "snap_2026_04_25",
        "calibration_version": "calib_v1",
        "judge_version": "judge_v1",
        "provenance_digest": "deadbeef",
        "candidate_routes": ("R1A", "R3", "R5"),
        "confidence_score": 0.92,
        "reason_codes": ("EXACT_CACHE_HIT",),
        "cost_usd": 0.0001,
        "latency_ms": 12,
        "extras": {"tier": "TIER_S"},
    }
    base.update(overrides)
    return DecisionEventRow(**base)


def test_ensure_schema_idempotent() -> None:
    """Repeated `ensure_schema` calls must not raise."""
    conn = _conn()
    ensure_schema(conn)
    ensure_schema(conn)
    ensure_schema(conn)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='decision_events'",
    )
    assert cur.fetchone() == ("decision_events",)


def test_insert_and_roundtrip_l0_row() -> None:
    """Insert one L0 row, read it back, fields preserved."""
    conn = _conn()
    ensure_schema(conn)
    row = _row()
    insert_decision_event(conn, row)
    fetched = conn.execute(
        "SELECT decision_layer, chosen_route, confidence_score, "
        "candidate_routes_json, reason_codes_json, extras_json, "
        "policy_hash, provenance_digest, outcome_success "
        "FROM decision_events WHERE decision_id = ?",
        (row.decision_id,),
    ).fetchone()
    assert fetched is not None
    (
        layer,
        chosen,
        conf,
        cand_json,
        reason_json,
        extras_json,
        policy_hash,
        prov_digest,
        outcome,
    ) = fetched
    assert layer == "L0_routing"
    assert chosen == "R1A"
    assert conf == pytest.approx(0.92)
    assert json.loads(cand_json) == ["R1A", "R3", "R5"]
    assert json.loads(reason_json) == ["EXACT_CACHE_HIT"]
    assert json.loads(extras_json) == {"tier": "TIER_S"}
    assert policy_hash == "policy_v1"
    assert prov_digest == "deadbeef"
    assert outcome is None  # decision-time row has no outcome yet


def test_all_known_layers_accepted() -> None:
    """Every label in ``DECISION_LAYERS`` must round-trip without raising."""
    conn = _conn()
    ensure_schema(conn)
    for layer in DECISION_LAYERS:
        row = _row(decision_id=str(uuid.uuid4()), decision_layer=layer)
        insert_decision_event(conn, row)
    count = conn.execute("SELECT COUNT(*) FROM decision_events").fetchone()[0]
    assert count == len(DECISION_LAYERS)


def test_unknown_layer_rejected() -> None:
    """``decision_layer`` outside the closed vocabulary raises."""
    conn = _conn()
    ensure_schema(conn)
    with pytest.raises(UnknownDecisionLayerError):
        insert_decision_event(conn, _row(decision_layer="L99_phantom"))


def test_outcome_backfill_via_replace() -> None:
    """Re-inserting the same ``decision_id`` updates ``outcome_success``."""
    conn = _conn()
    ensure_schema(conn)
    row = _row()
    insert_decision_event(conn, row)
    # Backfill — same id, outcome filled
    backfilled = _row(
        decision_id=row.decision_id,
        outcome_success=True,
        outcome_backfill_ts=time.time(),
    )
    insert_decision_event(conn, backfilled)
    outcome = conn.execute(
        "SELECT outcome_success FROM decision_events WHERE decision_id = ?",
        (row.decision_id,),
    ).fetchone()[0]
    assert outcome == 1
    # Still exactly one row — REPLACE semantics, not duplicate
    count = conn.execute(
        "SELECT COUNT(*) FROM decision_events WHERE decision_id = ?",
        (row.decision_id,),
    ).fetchone()[0]
    assert count == 1


def test_indexes_present() -> None:
    """All five indexes must exist after `ensure_schema`."""
    conn = _conn()
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='decision_events' "
        "AND name LIKE 'idx_de_%' "
        "ORDER BY name",
    ).fetchall()
    names = [r[0] for r in rows]
    assert "idx_de_timestamp" in names
    assert "idx_de_layer_app" in names
    assert "idx_de_provenance" in names
    assert "idx_de_outcome" in names
    assert "idx_de_request_hash" in names


def test_migration_from_legacy_table_empty_source() -> None:
    """No legacy rows → no migration target rows, returns 0."""
    conn = _conn()
    ensure_schema(conn)
    inserted = migrate_from_routing_decision_events(conn)
    assert inserted == 0


def test_migration_from_legacy_table_with_rows() -> None:
    """Migration copies legacy rows with `decision_layer='L0_routing'`."""
    conn = _conn()
    # Build a minimal legacy table
    conn.execute(
        """
        CREATE TABLE routing_decision_events (
            routing_trace_id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            app_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            gate_applied TEXT NOT NULL,
            gemini_subtier TEXT,
            cost_demoted INTEGER NOT NULL DEFAULT 0,
            target_model TEXT NOT NULL,
            confidence_score REAL,
            cost_usd REAL,
            cost_budget_remaining_usd REAL,
            latency_ms INTEGER,
            outcome_success INTEGER,
            dry_plan INTEGER NOT NULL DEFAULT 0,
            error_code TEXT,
            alias_source TEXT
        )
        """,
    )
    conn.execute(
        "INSERT INTO routing_decision_events VALUES "
        "('trace_1', 1700000000.0, 'app_a', 'TIER_S', 'gate_x', NULL, 0, "
        "'qwen-7b', 0.92, 0.0001, 1.0, 12, 1, 0, NULL, 'real')",
    )
    conn.execute(
        "INSERT INTO routing_decision_events VALUES "
        "('trace_2', 1700000001.0, 'app_b', 'TIER_M', 'gate_y', NULL, 1, "
        "'qwen-32b', 0.71, 0.001, 0.999, 245, NULL, 0, 'TIMEOUT', 'alias')",
    )
    conn.commit()

    inserted = migrate_from_routing_decision_events(conn)
    assert inserted == 2

    rows = conn.execute(
        "SELECT decision_id, decision_layer, chosen_route, error_code, extras_json "
        "FROM decision_events ORDER BY decision_id",
    ).fetchall()
    assert len(rows) == 2
    assert all(r[1] == "L0_routing" for r in rows)
    assert rows[0][0] == "trace_1"
    assert rows[0][2] == "TIER_S"
    assert rows[1][3] == "TIMEOUT"
    extras_2 = json.loads(rows[1][4])
    assert extras_2["alias_source"] == "alias"
    assert extras_2["migrated_from"] == "routing_decision_events"


def test_migration_idempotent() -> None:
    """Running migration twice does not duplicate rows."""
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE routing_decision_events (
            routing_trace_id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            app_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            gate_applied TEXT NOT NULL,
            gemini_subtier TEXT,
            cost_demoted INTEGER NOT NULL DEFAULT 0,
            target_model TEXT NOT NULL,
            confidence_score REAL,
            cost_usd REAL,
            cost_budget_remaining_usd REAL,
            latency_ms INTEGER,
            outcome_success INTEGER,
            dry_plan INTEGER NOT NULL DEFAULT 0,
            error_code TEXT,
            alias_source TEXT
        )
        """,
    )
    conn.execute(
        "INSERT INTO routing_decision_events VALUES "
        "('trace_dup', 1700000000.0, 'app_a', 'TIER_S', 'gate_x', NULL, 0, "
        "'qwen-7b', 0.5, 0.0001, 1.0, 12, NULL, 0, NULL, NULL)",
    )
    conn.commit()
    first = migrate_from_routing_decision_events(conn)
    second = migrate_from_routing_decision_events(conn)
    assert first == 1
    assert second == 0
    count = conn.execute("SELECT COUNT(*) FROM decision_events").fetchone()[0]
    assert count == 1

"""Schema module for the ``routing_decision_events`` table (Wave F2 M3).

ADR-025 §3 defines the canonical relational projection of
``heal_router.v1`` spans. This module holds the DDL as a string constant
plus a helper to create the table on a given `sqlite3.Connection`.

M3 scope (this file):
- Provide the CREATE TABLE / CREATE INDEX DDL
- Provide ``ensure_schema(conn)`` for idempotent creation
- Provide ``insert_record(conn, record)`` for a single `RoutingSpanRecord`

M3 out of scope (future work with its own parent plan):
- Wiring into ``tools/generate_full_adg.py`` so the ADG build ingests spans
- Migrating ``tools/routing/calibrate_thresholds.py`` from JSONL to this table
- Building the ``mv_routing_*`` materialized views (see RCA H9)

Plan references: ADR-025 §3 §4 (Phase M3); routing-followups-7a2c91.md.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import sqlite3

    from .heal_router_otel import RoutingSpanRecord


ROUTING_DECISION_EVENTS_DDL: str = """
CREATE TABLE IF NOT EXISTS routing_decision_events (
    routing_trace_id          TEXT PRIMARY KEY,
    timestamp                 REAL NOT NULL,
    app_name                  TEXT NOT NULL,
    tier                      TEXT NOT NULL,
    gate_applied              TEXT NOT NULL,
    gemini_subtier            TEXT,
    cost_demoted              INTEGER NOT NULL DEFAULT 0,
    target_model              TEXT NOT NULL,
    confidence_score          REAL,
    cost_usd                  REAL,
    cost_budget_remaining_usd REAL,
    latency_ms                INTEGER,
    outcome_success           INTEGER,
    dry_plan                  INTEGER NOT NULL DEFAULT 0,
    error_code                TEXT,
    alias_source              TEXT
);
""".strip()

ROUTING_DECISION_EVENTS_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_routing_timestamp ON routing_decision_events(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_routing_app_tier ON routing_decision_events(app_name, tier);",
    "CREATE INDEX IF NOT EXISTS idx_routing_gate ON routing_decision_events(gate_applied);",
)


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotently create the routing_decision_events table and indexes."""
    cur = conn.cursor()
    cur.execute(ROUTING_DECISION_EVENTS_DDL)
    for stmt in ROUTING_DECISION_EVENTS_INDEXES:
        cur.execute(stmt)
    conn.commit()


def insert_record(conn: sqlite3.Connection, record: RoutingSpanRecord) -> None:
    """Insert one RoutingSpanRecord. Uses INSERT OR REPLACE on trace_id.

    The `alias_source` column is populated from
    ``record.extra_attributes["routing.alias_source"]`` when present; this
    lets consumers distinguish real route spans from legacy-alias feeders
    (Wave F2 M2).
    """
    alias_source = record.extra_attributes.get("routing.alias_source") if record.extra_attributes else None
    conn.execute(
        """
        INSERT OR REPLACE INTO routing_decision_events (
            routing_trace_id, timestamp, app_name, tier, gate_applied,
            gemini_subtier, cost_demoted, target_model, confidence_score,
            cost_usd, cost_budget_remaining_usd, latency_ms, outcome_success,
            dry_plan, error_code, alias_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.routing_trace_id,
            record.timestamp,
            record.app_name,
            record.tier,
            record.gate_applied,
            record.gemini_subtier or None,
            1 if record.cost_demoted else 0,
            record.target_model,
            record.confidence_score,
            record.cost_usd,
            record.cost_budget_remaining_usd,
            record.latency_ms,
            None if record.outcome_success is None else (1 if record.outcome_success else 0),
            1 if record.dry_plan else 0,
            record.error_code,
            alias_source,
        ),
    )
    conn.commit()


__all__ = [
    "ROUTING_DECISION_EVENTS_DDL",
    "ROUTING_DECISION_EVENTS_INDEXES",
    "ensure_schema",
    "insert_record",
]

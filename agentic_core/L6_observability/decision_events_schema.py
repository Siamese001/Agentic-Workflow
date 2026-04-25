"""Unified `decision_events` table — cross-layer relational projection.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W1.

Supersedes the L0-only ``routing_decision_events`` table (ADR-025 §3 / Wave F2 M3
in ``routing_decision_events_schema.py``) by partitioning rows on ``decision_layer``
so every routing-class decision across the architecture lands in one queryable
relational surface:

* ``L0_routing``    — RouteContract dispatch (R1A/R1B/R3/R4/R5)
* ``L1_reasoning``  — plan-generation routing (clarify / decompose / proceed)
* ``C0_retrieval``  — retrieval-mode routing (dense / sparse / graph / hybrid)
* ``PA_assembly``   — Prompt Assembly authority-order routing
* ``L2_execution``  — R-CASC tier escalation (TIER_S/M/L/HITL)
* ``L3_orchestration`` — workflow-shape routing (DAG / cascade / loop)
* ``L5_safety``     — HITL / guardrail escalation
* ``Exit_eval``     — allow / deny / reroute / escalate / commit-request
* ``UWG``           — durable-write commit decision
* ``L6_promotion``  — shadow → canary → prod promotion routing

Provenance fields are NOT NULL except ``outcome_success``, which is populated
by the W2 outcome-backfill API after Exit Eval seals.

This module is deliberately additive — the legacy ``routing_decision_events``
table is preserved by ``routing_decision_events_schema.py`` and a one-shot
migration helper here copies its rows into the unified surface with
``decision_layer = 'L0_routing'``.

References:
- Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md``
- Predecessor: ``agentic_core/L6_observability/routing_decision_events_schema.py``
- ADR-025 §3 (relational projection of ``heal_router.v1`` spans)
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from typing import Any, Final

# ---------------------------------------------------------------------------
# Closed-vocabulary layer labels — DO NOT ADD without a corresponding ADR.
# ---------------------------------------------------------------------------

DECISION_LAYERS: Final[frozenset[str]] = frozenset(
    {
        "L0_routing",
        "L1_reasoning",
        "C0_retrieval",
        "PA_assembly",
        "L2_execution",
        "L3_orchestration",
        "L5_safety",
        "Exit_eval",
        "UWG",
        "L6_promotion",
    },
)


# ---------------------------------------------------------------------------
# DDL — single canonical table for all decision-class events.
# ---------------------------------------------------------------------------

DECISION_EVENTS_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS decision_events (
    decision_id               TEXT PRIMARY KEY,
    timestamp                 REAL    NOT NULL,
    decision_layer            TEXT    NOT NULL,
    app_name                  TEXT    NOT NULL,
    request_hash              TEXT    NOT NULL,
    chosen_route              TEXT    NOT NULL,
    candidate_routes_json     TEXT    NOT NULL DEFAULT '[]',
    confidence_score          REAL,
    reason_codes_json         TEXT    NOT NULL DEFAULT '[]',
    cost_usd                  REAL,
    latency_ms                INTEGER,
    outcome_success           INTEGER,
    outcome_backfill_ts       REAL,
    error_code                TEXT,
    -- Provenance (W3) ------------------------------------------------------
    policy_hash               TEXT    NOT NULL,
    snapshot_id               TEXT    NOT NULL,
    calibration_version       TEXT    NOT NULL,
    judge_version             TEXT    NOT NULL,
    provenance_digest         TEXT    NOT NULL,
    -- Free-form extras (small JSON) ---------------------------------------
    extras_json               TEXT    NOT NULL DEFAULT '{}',
    CONSTRAINT decision_layer_known CHECK (
        decision_layer IN (
            'L0_routing','L1_reasoning','C0_retrieval','PA_assembly',
            'L2_execution','L3_orchestration','L5_safety','Exit_eval',
            'UWG','L6_promotion'
        )
    )
);
""".strip()

DECISION_EVENTS_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS idx_de_timestamp ON decision_events(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_de_layer_app ON decision_events(decision_layer, app_name);",
    "CREATE INDEX IF NOT EXISTS idx_de_provenance ON decision_events(policy_hash, snapshot_id);",
    "CREATE INDEX IF NOT EXISTS idx_de_outcome ON decision_events(outcome_success);",
    "CREATE INDEX IF NOT EXISTS idx_de_request_hash ON decision_events(request_hash);",
)


# ---------------------------------------------------------------------------
# Row dataclass — typed surface for inserts.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DecisionEventRow:
    """One row in the unified ``decision_events`` table.

    Fields mirror the DDL. ``candidate_routes`` / ``reason_codes`` / ``extras``
    are lists / dicts that the writer serializes to JSON before the SQL
    insert. ``outcome_success`` is left None at decision time and populated
    later by the W2 backfill API.
    """

    decision_id: str
    timestamp: float
    decision_layer: str
    app_name: str
    request_hash: str
    chosen_route: str
    policy_hash: str
    snapshot_id: str
    calibration_version: str
    judge_version: str
    provenance_digest: str
    candidate_routes: tuple[str, ...] = ()
    confidence_score: float | None = None
    reason_codes: tuple[str, ...] = ()
    cost_usd: float | None = None
    latency_ms: int | None = None
    outcome_success: bool | None = None
    outcome_backfill_ts: float | None = None
    error_code: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)


class UnknownDecisionLayerError(ValueError):
    """Raised when ``decision_layer`` is not in ``DECISION_LAYERS``."""


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotently create the ``decision_events`` table and indexes.

    Safe to call on every process start. Uses ``CREATE TABLE IF NOT EXISTS``
    so concurrent calls from multiple workers will not raise.
    """
    cur = conn.cursor()
    cur.execute(DECISION_EVENTS_DDL)
    for stmt in DECISION_EVENTS_INDEXES:
        cur.execute(stmt)
    conn.commit()


def insert_decision_event(conn: sqlite3.Connection, row: DecisionEventRow) -> None:
    """Insert one ``DecisionEventRow``. ``decision_id`` is the primary key.

    Uses ``INSERT OR REPLACE`` so an upsert on the same ``decision_id`` is
    explicit (not silent). Callers that want strict uniqueness should pass
    a fresh UUID per decision.

    Raises:
        UnknownDecisionLayerError: when ``row.decision_layer`` is outside the
            closed vocabulary in ``DECISION_LAYERS``.
    """
    if row.decision_layer not in DECISION_LAYERS:
        raise UnknownDecisionLayerError(
            f"unknown decision_layer={row.decision_layer!r}; allowed={sorted(DECISION_LAYERS)}",
        )
    payload = asdict(row)
    # Lists / dicts → JSON
    payload["candidate_routes_json"] = json.dumps(
        list(row.candidate_routes),
        separators=(",", ":"),
    )
    payload["reason_codes_json"] = json.dumps(
        list(row.reason_codes),
        separators=(",", ":"),
    )
    payload["extras_json"] = json.dumps(row.extras, separators=(",", ":"), sort_keys=True)
    # outcome_success bool → int|None
    outcome_int: int | None
    if row.outcome_success is None:
        outcome_int = None
    else:
        outcome_int = 1 if row.outcome_success else 0
    conn.execute(
        """
        INSERT OR REPLACE INTO decision_events (
            decision_id, timestamp, decision_layer, app_name, request_hash,
            chosen_route, candidate_routes_json, confidence_score,
            reason_codes_json, cost_usd, latency_ms,
            outcome_success, outcome_backfill_ts, error_code,
            policy_hash, snapshot_id, calibration_version, judge_version,
            provenance_digest, extras_json
        ) VALUES (
            :decision_id, :timestamp, :decision_layer, :app_name, :request_hash,
            :chosen_route, :candidate_routes_json, :confidence_score,
            :reason_codes_json, :cost_usd, :latency_ms,
            :outcome_success_int, :outcome_backfill_ts, :error_code,
            :policy_hash, :snapshot_id, :calibration_version, :judge_version,
            :provenance_digest, :extras_json
        )
        """,
        {
            **payload,
            "outcome_success_int": outcome_int,
        },
    )
    conn.commit()


def migrate_from_routing_decision_events(conn: sqlite3.Connection) -> int:
    """One-shot migration of legacy ``routing_decision_events`` rows.

    Copies every row from the legacy ADR-025 §3 table into the unified
    ``decision_events`` table with ``decision_layer = 'L0_routing'`` and
    sentinel provenance fields ('legacy') for the four W3 columns that did
    not exist on the source schema.

    Idempotent — re-running yields zero new rows because ``decision_id``
    is the primary key on the destination.

    Returns:
        Number of rows actually inserted (excludes existing-PK skips).
    """
    ensure_schema(conn)
    cur = conn.cursor()
    # Legacy table may not exist (fresh deploy). Tolerate that.
    try:
        cur.execute("SELECT COUNT(*) FROM routing_decision_events")
    except sqlite3.OperationalError:
        return 0
    inserted = 0
    rows = cur.execute(
        """
        SELECT routing_trace_id, timestamp, app_name, tier, gate_applied,
               target_model, confidence_score, cost_usd,
               latency_ms, outcome_success, error_code, alias_source
        FROM routing_decision_events
        """,
    ).fetchall()
    for r in rows:
        (
            trace_id,
            ts,
            app_name,
            tier,
            gate_applied,
            target_model,
            conf,
            cost,
            latency,
            outcome,
            err,
            alias_source,
        ) = r
        existing = cur.execute(
            "SELECT 1 FROM decision_events WHERE decision_id = ?",
            (trace_id,),
        ).fetchone()
        if existing:
            continue
        extras = {
            "tier": tier,
            "gate_applied": gate_applied,
            "target_model": target_model,
            "alias_source": alias_source,
            "migrated_from": "routing_decision_events",
        }
        outcome_bool: bool | None
        if outcome is None:
            outcome_bool = None
        else:
            outcome_bool = bool(outcome)
        legacy_row = DecisionEventRow(
            decision_id=trace_id,
            timestamp=ts,
            decision_layer="L0_routing",
            app_name=app_name,
            request_hash="legacy",
            chosen_route=tier or "unknown",
            policy_hash="legacy",
            snapshot_id="legacy",
            calibration_version="legacy",
            judge_version="legacy",
            provenance_digest="legacy",
            confidence_score=conf,
            cost_usd=cost,
            latency_ms=latency,
            outcome_success=outcome_bool,
            error_code=err,
            extras=extras,
        )
        insert_decision_event(conn, legacy_row)
        inserted += 1
    return inserted


__all__ = [
    "DECISION_EVENTS_DDL",
    "DECISION_EVENTS_INDEXES",
    "DECISION_LAYERS",
    "DecisionEventRow",
    "UnknownDecisionLayerError",
    "ensure_schema",
    "insert_decision_event",
    "migrate_from_routing_decision_events",
]

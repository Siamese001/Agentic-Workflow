"""REQ Coverage Exemplar Ledger writer.

Stores OTEL-style exemplars linking each REQ_ID coverage assertion to a
specific (trace_id, span_id) instance observed at runtime. SQLite-backed,
fail-soft (never raises into the caller — observability writes must not
crash the host process).

Schema design notes:
  * One row per (req_id, layer, edge_kind, trace_id) tuple seen in a flush.
  * Indexed on (req_id, observed_at DESC) for the freshness query
    (the dominant CI-gate pattern).
  * Indexed on (trace_id) for trace→REQ joins (rare but cheap).
  * Indexed on (app_id, observed_at DESC) for per-app dashboards.

Industry references:
  * OpenTelemetry exemplars — bidirectional metric↔trace link.
  * ISO 26262 Requirements Traceability Matrix — the formal pattern.
  * Pact-style consumer-driven contracts — verifier reads this ledger.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from collections import Counter
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

DEFAULT_LEDGER_PATH = (
    Path(__file__).resolve().parents[2] / "artifacts" / "runtime" / "req_emission_ledger.sqlite"
)

_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS req_emission (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id          TEXT    NOT NULL,
    trace_id        TEXT    NOT NULL,
    span_id         TEXT,
    layer           TEXT    NOT NULL,
    edge_kind       TEXT    NOT NULL,
    app_id          TEXT    NOT NULL,
    span_count      INTEGER NOT NULL DEFAULT 1,
    observed_at     INTEGER NOT NULL,
    source          TEXT    NOT NULL,
    schema_version  INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_req      ON req_emission (req_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_trace    ON req_emission (trace_id);
CREATE INDEX IF NOT EXISTS idx_app      ON req_emission (app_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_layer    ON req_emission (layer, observed_at DESC);
"""


def ensure_schema(db_path: Path | str = DEFAULT_LEDGER_PATH) -> None:
    """Create the ledger DB and indices if they don't exist. Idempotent.

    Accepts either ``Path`` or ``str`` for ``db_path``; strings are coerced
    so callers from subprocess scripts (where paths are interpolated as
    strings) work without surprises.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as con:
        con.executescript(_SCHEMA_DDL)
        con.commit()


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open the ledger with WAL + busy timeout; yield the connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path, timeout=10.0)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        yield con
    finally:
        con.close()


def _extract_exemplars(span: dict[str, Any], app_id: str, source: str) -> list[tuple]:
    """Convert one span dict into 0..N ledger rows.

    A span produces one row per req_id it carries. Spans without `req_ids`
    in their attributes are NOT recorded (silence-by-default — the ledger
    is for explicit REQ binding only).
    """
    attrs: dict[str, Any] = span.get("attributes") or {}
    req_ids_raw = (
        attrs.get("agentic.req.ids")
        or attrs.get("req_ids")
        or ()
    )
    if isinstance(req_ids_raw, str):
        req_ids = tuple(s.strip() for s in req_ids_raw.split(",") if s.strip())
    else:
        req_ids = tuple(req_ids_raw or ())
    if not req_ids:
        return []

    trace_id = span.get("trace_id") or attrs.get("trace_id") or ""
    span_id = span.get("span_id") or attrs.get("span_id")
    layer = (
        attrs.get("agentic.req.layer")
        or attrs.get("layer")
        or span.get("layer")
        or "unknown"
    )
    edge_kind = (
        attrs.get("agentic.req.edge_kind")
        or attrs.get("edge_kind")
        or span.get("name", "unknown").removeprefix("adg.")
    )
    observed_at = int(span.get("observed_at") or time.time())

    return [
        (
            req_id,
            trace_id,
            span_id,
            str(layer),
            str(edge_kind),
            app_id,
            1,
            observed_at,
            source,
            SCHEMA_VERSION,
        )
        for req_id in req_ids
    ]


def write_emissions(
    spans: Iterable[dict[str, Any]],
    *,
    app_id: str,
    source: str,
    db_path: Path | str = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    """Persist REQ exemplars from buffered spans.

    Fail-soft: catches sqlite errors and returns ``{"success": False, ...}``
    instead of raising. Returns ``{"success": True, "rows_written": N,
    "distinct_req_ids": M}`` on success. Accepts ``str`` or ``Path`` for
    ``db_path`` (coerced internally).
    """
    db_path = Path(db_path)
    rows: list[tuple] = []
    for span in spans:
        try:
            rows.extend(_extract_exemplars(span, app_id=app_id, source=source))
        except (KeyError, TypeError, ValueError) as exc:
            # Malformed individual span — log and skip, keep going.
            logger.warning("ledger_writer: skipped malformed span: %s", exc)

    if not rows:
        return {"success": True, "rows_written": 0, "distinct_req_ids": 0}

    try:
        ensure_schema(db_path)
        with _connect(db_path) as con:
            con.executemany(
                """
                INSERT INTO req_emission
                  (req_id, trace_id, span_id, layer, edge_kind, app_id,
                   span_count, observed_at, source, schema_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            con.commit()
    except sqlite3.Error as exc:
        logger.warning("ledger_writer: sqlite error, evidence not persisted: %s", exc)
        return {"success": False, "error": str(exc), "rows_attempted": len(rows)}

    distinct_reqs = len({r[0] for r in rows})
    return {
        "success": True,
        "rows_written": len(rows),
        "distinct_req_ids": distinct_reqs,
        "ledger_path": str(db_path),
    }


class LedgerWriter:
    """Object-oriented wrapper around :func:`write_emissions`.

    Intended for callers that hold a long-lived emitter (e.g. the
    OTEL lifecycle bridge) and want a stable instance to call
    ``writer.write(spans)`` against.
    """

    def __init__(
        self,
        *,
        app_id: str,
        source: str,
        db_path: Path = DEFAULT_LEDGER_PATH,
    ) -> None:
        self.app_id = app_id
        self.source = source
        self.db_path = db_path

    def write(self, spans: Iterable[dict[str, Any]]) -> dict[str, Any]:
        return write_emissions(
            spans, app_id=self.app_id, source=self.source, db_path=self.db_path,
        )

    def query_freshness(
        self,
        *,
        within_seconds: int = 7 * 24 * 3600,
        db_path: Path | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Per-REQ_ID summary of recent activity.

        Returns ``{req_id: {"count": N, "latest": unix_ts, "apps": [...]}}``.
        """
        path = db_path or self.db_path
        cutoff = int(time.time()) - within_seconds
        with closing(sqlite3.connect(path)) as con:
            cur = con.execute(
                """
                SELECT req_id, COUNT(*), MAX(observed_at),
                       GROUP_CONCAT(DISTINCT app_id),
                       GROUP_CONCAT(DISTINCT layer)
                FROM req_emission
                WHERE observed_at >= ?
                GROUP BY req_id
                """,
                (cutoff,),
            )
            return {
                row[0]: {
                    "count": row[1],
                    "latest": row[2],
                    "apps": (row[3] or "").split(","),
                    "layers": (row[4] or "").split(","),
                }
                for row in cur.fetchall()
            }


def stats(db_path: Path = DEFAULT_LEDGER_PATH) -> dict[str, Any]:
    """Quick health snapshot: total rows, distinct REQs, latest observed_at."""
    if not db_path.exists():
        return {"exists": False, "rows": 0, "distinct_req_ids": 0}
    with closing(sqlite3.connect(db_path)) as con:
        total = con.execute("SELECT COUNT(*) FROM req_emission").fetchone()[0]
        distinct = con.execute(
            "SELECT COUNT(DISTINCT req_id) FROM req_emission"
        ).fetchone()[0]
        latest = con.execute(
            "SELECT MAX(observed_at) FROM req_emission"
        ).fetchone()[0]
        per_app = Counter(
            row[0]
            for row in con.execute(
                "SELECT app_id FROM req_emission ORDER BY observed_at DESC LIMIT 5000"
            )
        )
    return {
        "exists": True,
        "rows": total,
        "distinct_req_ids": distinct,
        "latest_observed_at": latest,
        "top_apps": per_app.most_common(10),
    }

"""tools.ledgers.consulter — Precedent lookup across any intelligence ledger.

Contract mirrors the existing refactor-decision-memory skill:

    c = LedgerConsulter("tool_routing")
    verdict = c.lookup(
        query_text="imports of semantic_enricher across apps_*",
        filters={"event_kind": "retrieval_tool_choice"},
        limit=5,
    )
    # verdict.strength in {"strong", "suggestive", "none"}
    # verdict.matches is a list of dicts (top-N rows)

Design rules:
    - Pure-read. Never mutates the ledger DB.
    - Stdlib only.
    - Falls back gracefully if FTS5 unavailable (uses LIKE on repo_area +
      event_kind instead).
    - Strength verdict:
        strong      = ≥1 match with score_band in {"P1","strong","correct"}
                      AND top match FTS bm25 rank ≤ -8.0 (well above noise)
        suggestive  = ≥1 match but only weak bands OR marginal FTS score
        none        = no rows match filter
"""

from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Any

from tools.ledgers.schema_registry import get

# Strong-signal score bands across all ledgers (extend per ledger as needed)
_STRONG_BANDS = frozenset({"P1", "P2", "strong", "correct", "hit", "aligned"})
_WEAK_BANDS = frozenset({"P4", "P5", "weak", "miss", "drift"})


@dataclass
class PrecedentVerdict:
    strength: str  # "strong" | "suggestive" | "none"
    matches: list[dict[str, Any]] = field(default_factory=list)
    total_rows_examined: int = 0
    ledger: str = ""
    fts_available: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "strength": self.strength,
            "match_count": len(self.matches),
            "total_rows_examined": self.total_rows_examined,
            "ledger": self.ledger,
            "fts_available": self.fts_available,
            "matches": self.matches,
        }


class LedgerConsulter:
    """Read-only precedent lookup for one ledger."""

    def __init__(self, ledger_name: str) -> None:
        self.spec = get(ledger_name)
        self.db_path = self.spec.db_path

    # ------------------------------------------------------------------ #
    def lookup(
        self,
        *,
        query_text: str = "",
        filters: dict[str, Any] | None = None,
        limit: int = 5,
    ) -> PrecedentVerdict:
        """Query the ledger for precedent rows matching query + filters.

        Returns PrecedentVerdict with strength classification and top-N matches.
        """
        filters = filters or {}
        limit = max(1, min(limit, 50))
        verdict = PrecedentVerdict(strength="none", ledger=self.spec.name)

        if not self.db_path.exists():
            return verdict

        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5)
            conn.row_factory = sqlite3.Row
            try:
                verdict.fts_available = self._fts_available(conn)
                if verdict.fts_available and query_text.strip():
                    rows = self._fts_search(conn, query_text, filters, limit)
                else:
                    rows = self._like_search(conn, query_text, filters, limit)

                verdict.matches = [self._row_to_dict(r) for r in rows]
                verdict.total_rows_examined = self._count_candidates(conn, filters)
                verdict.strength = self._grade(verdict.matches)
            finally:
                conn.close()
        except sqlite3.Error as exc:
            print(
                f"[ledger.consulter] {self.spec.name} lookup failed: {exc}",
                file=sys.stderr,
            )
        return verdict

    # ------------------------------------------------------------------ #
    @staticmethod
    def _fts_available(conn: sqlite3.Connection) -> bool:
        cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='events_fts'")
        return cur.fetchone() is not None

    @staticmethod
    def _where_from_filters(filters: dict[str, Any]) -> tuple[str, list[Any]]:
        clauses = []
        params: list[Any] = []
        for key in (
            "event_kind",
            "repo_area",
            "branch",
            "commit_sha",
            "adg_snapshot_id",
            "score_band",
            "status",
            "session_id",
        ):
            val = filters.get(key)
            if val:
                clauses.append(f"e.{key} = ?")
                params.append(val)
        since = filters.get("since_ts")
        if since:
            clauses.append("e.ts_utc >= ?")
            params.append(since)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        return where, params

    def _fts_search(
        self,
        conn: sqlite3.Connection,
        query_text: str,
        filters: dict[str, Any],
        limit: int,
    ) -> list[sqlite3.Row]:
        where, params = self._where_from_filters(filters)
        # FTS MATCH requires a safe-ish query string; strip quotes to avoid syntax errors
        safe_query = query_text.replace('"', " ").strip()
        sql = f"""
            SELECT e.*, fts.rank AS fts_rank
              FROM events_fts fts
              JOIN events e ON e.rowid = fts.rowid
             WHERE events_fts MATCH ?
             {where.replace("WHERE", "AND") if where else ""}
             ORDER BY fts.rank
             LIMIT ?
        """
        return list(conn.execute(sql, [safe_query, *params, limit]))

    def _like_search(
        self,
        conn: sqlite3.Connection,
        query_text: str,
        filters: dict[str, Any],
        limit: int,
    ) -> list[sqlite3.Row]:
        where, params = self._where_from_filters(filters)
        like_clause = ""
        if query_text.strip():
            like_clause = " AND (e.repo_area LIKE ? OR e.prediction_json LIKE ? OR e.outcome_json LIKE ?)"
            like_param = f"%{query_text.strip()}%"
            params.extend([like_param, like_param, like_param])
        sql = f"""
            SELECT e.*, NULL AS fts_rank
              FROM events e
             {where or "WHERE 1=1"}
             {like_clause}
             ORDER BY e.ts_utc DESC
             LIMIT ?
        """
        params.append(limit)
        return list(conn.execute(sql, params))

    def _count_candidates(self, conn: sqlite3.Connection, filters: dict[str, Any]) -> int:
        where, params = self._where_from_filters(filters)
        sql = f"SELECT COUNT(*) FROM events e {where}"
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        return int(row[0]) if row else 0

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {k: row[k] for k in row.keys()}

    @staticmethod
    def _grade(matches: list[dict[str, Any]]) -> str:
        if not matches:
            return "none"
        top = matches[0]
        band = (top.get("score_band") or "").strip()
        rank = top.get("fts_rank")
        if band in _STRONG_BANDS:
            if rank is None or rank <= -8.0:
                return "strong"
            return "suggestive"
        if band in _WEAK_BANDS:
            return "suggestive"
        # Band is neutral/unknown — grade by volume
        return "suggestive" if len(matches) >= 3 else "suggestive"

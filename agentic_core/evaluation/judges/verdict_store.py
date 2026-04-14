"""Verdict Store — persistent SQLite-backed storage for judge verdicts.

Provides durable storage for all judge verdicts with:
- Per-module, per-dimension, per-rubric queries
- Trend analysis (score history over ADG rebuilds)
- Regression detection between ADG digests
- Evidence item storage linked to verdicts

Usage::

    store = VerdictStore("artifacts/judge/verdicts.sqlite")
    store.store_verdict(verdict)
    history = store.query_by_module("agentic_core/L2_execution/providers.py")
    trend = store.trend("agentic_core/L2_execution/providers.py", "write_governance", n=10)
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.evaluation.judges.types import (
    JudgeVerdict,
    VerdictOutcome,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0.0"

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verdicts (
    verdict_id    TEXT PRIMARY KEY,
    target        TEXT NOT NULL,
    dimension     TEXT NOT NULL,
    rubric_id     TEXT NOT NULL,
    outcome       TEXT NOT NULL,
    score         REAL NOT NULL,
    reasoning     TEXT NOT NULL DEFAULT '',
    severity      TEXT NOT NULL DEFAULT 'MEDIUM',
    adg_digest    TEXT NOT NULL DEFAULT '',
    provider_id   TEXT NOT NULL DEFAULT '',
    evidence_hash TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verdict_evidence (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    verdict_id    TEXT NOT NULL REFERENCES verdicts(verdict_id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    key           TEXT NOT NULL,
    value         TEXT NOT NULL,
    file_path     TEXT NOT NULL DEFAULT '',
    line_no       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS verdict_suggestions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    verdict_id TEXT NOT NULL REFERENCES verdicts(verdict_id) ON DELETE CASCADE,
    suggestion TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_verdicts_target ON verdicts(target);
CREATE INDEX IF NOT EXISTS idx_verdicts_dimension ON verdicts(dimension);
CREATE INDEX IF NOT EXISTS idx_verdicts_rubric ON verdicts(rubric_id);
CREATE INDEX IF NOT EXISTS idx_verdicts_digest ON verdicts(adg_digest);
CREATE INDEX IF NOT EXISTS idx_verdicts_outcome ON verdicts(outcome);
CREATE INDEX IF NOT EXISTS idx_verdicts_created ON verdicts(created_at);
CREATE INDEX IF NOT EXISTS idx_evidence_verdict ON verdict_evidence(verdict_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_verdict ON verdict_suggestions(verdict_id);
"""


class VerdictStore:
    """Persistent SQLite-backed verdict storage.

    Thread-safe for single-writer usage. Each method opens and closes
    its own transaction.
    """

    def __init__(self, db_path: str = "artifacts/judge/verdicts.sqlite") -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._connect()
        try:
            conn.executescript(_CREATE_TABLES)
            conn.execute(
                "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
                ("schema_version", _SCHEMA_VERSION),
            )
            conn.commit()
            _log.info("[VerdictStore] Initialized at %s", self._db_path)
        finally:
            conn.close()

    def store_verdict(self, verdict: JudgeVerdict) -> None:
        """Persist a single verdict with its evidence and suggestions."""
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO verdicts
                   (verdict_id, target, dimension, rubric_id, outcome,
                    score, reasoning, severity, adg_digest, provider_id,
                    evidence_hash, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    verdict.verdict_id,
                    verdict.target,
                    verdict.dimension,
                    verdict.rubric_id,
                    verdict.outcome,
                    verdict.score,
                    verdict.reasoning,
                    verdict.severity,
                    verdict.adg_digest,
                    verdict.provider_id,
                    verdict.evidence_hash,
                    verdict.created_at or datetime.now(timezone.utc).isoformat(),
                ),
            )

            conn.execute(
                "DELETE FROM verdict_evidence WHERE verdict_id = ?",
                (verdict.verdict_id,),
            )
            for item in tqdm(verdict.evidence_items, desc="Processing", unit="item"):
                conn.execute(
                    """INSERT INTO verdict_evidence
                       (verdict_id, evidence_type, key, value, file_path, line_no)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        verdict.verdict_id,
                        item.evidence_type,
                        item.key,
                        item.value,
                        item.file_path,
                        item.line_no,
                    ),
                )

            conn.execute(
                "DELETE FROM verdict_suggestions WHERE verdict_id = ?",
                (verdict.verdict_id,),
            )
            for suggestion in verdict.suggestions:
                conn.execute(
                    "INSERT INTO verdict_suggestions (verdict_id, suggestion) VALUES (?, ?)",
                    (verdict.verdict_id, suggestion),
                )

            conn.commit()
        finally:
            conn.close()

    def store_verdicts(self, verdicts: list[JudgeVerdict]) -> int:
        """Persist multiple verdicts in a single transaction. Returns count stored."""
        conn = self._connect()
        count = 0
        try:
            for verdict in tqdm(verdicts, desc="Processing", unit="item"):
                conn.execute(
                    """INSERT OR REPLACE INTO verdicts
                       (verdict_id, target, dimension, rubric_id, outcome,
                        score, reasoning, severity, adg_digest, provider_id,
                        evidence_hash, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        verdict.verdict_id,
                        verdict.target,
                        verdict.dimension,
                        verdict.rubric_id,
                        verdict.outcome,
                        verdict.score,
                        verdict.reasoning,
                        verdict.severity,
                        verdict.adg_digest,
                        verdict.provider_id,
                        verdict.evidence_hash,
                        verdict.created_at or datetime.now(timezone.utc).isoformat(),
                    ),
                )
                count += 1

            conn.commit()
        finally:
            conn.close()

        return count

    def _row_to_verdict(self, row: sqlite3.Row) -> JudgeVerdict:
        """Convert a DB row to a JudgeVerdict (without evidence/suggestions for speed)."""
        return JudgeVerdict(
            verdict_id=row["verdict_id"],
            target=row["target"],
            dimension=row["dimension"],
            rubric_id=row["rubric_id"],
            outcome=row["outcome"],
            score=row["score"],
            reasoning=row["reasoning"],
            severity=row["severity"],
            adg_digest=row["adg_digest"],
            provider_id=row["provider_id"],
            evidence_hash=row["evidence_hash"],
            created_at=row["created_at"],
        )

    def query_by_module(
        self,
        module_path: str,
        limit: int = 100,
    ) -> list[JudgeVerdict]:
        """Get all verdicts for a specific module."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM verdicts WHERE target = ? ORDER BY created_at DESC LIMIT ?",
                (module_path, limit),
            ).fetchall()
            return [self._row_to_verdict(r) for r in rows]
        finally:
            conn.close()

    def query_by_dimension(
        self,
        dimension: str,
        limit: int = 100,
    ) -> list[JudgeVerdict]:
        """Get all verdicts for a specific dimension."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM verdicts WHERE dimension = ? ORDER BY created_at DESC LIMIT ?",
                (dimension, limit),
            ).fetchall()
            return [self._row_to_verdict(r) for r in rows]
        finally:
            conn.close()

    def query_by_rubric(
        self,
        rubric_id: str,
        limit: int = 100,
    ) -> list[JudgeVerdict]:
        """Get all verdicts for a specific rubric."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM verdicts WHERE rubric_id = ? ORDER BY created_at DESC LIMIT ?",
                (rubric_id, limit),
            ).fetchall()
            return [self._row_to_verdict(r) for r in rows]
        finally:
            conn.close()

    def query_by_digest(
        self,
        adg_digest: str,
        limit: int = 500,
    ) -> list[JudgeVerdict]:
        """Get all verdicts for a specific ADG digest (one evaluation run)."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM verdicts WHERE adg_digest = ? ORDER BY target, dimension LIMIT ?",
                (adg_digest, limit),
            ).fetchall()
            return [self._row_to_verdict(r) for r in rows]
        finally:
            conn.close()

    def query_failures(
        self,
        adg_digest: str = "",
        limit: int = 100,
    ) -> list[JudgeVerdict]:
        """Get all FAIL verdicts, optionally filtered by digest."""
        conn = self._connect()
        try:
            if adg_digest:
                rows = conn.execute(
                    """SELECT * FROM verdicts
                       WHERE outcome = ? AND adg_digest = ?
                       ORDER BY severity, target LIMIT ?""",
                    (VerdictOutcome.FAIL.value, adg_digest, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM verdicts
                       WHERE outcome = ?
                       ORDER BY created_at DESC, severity LIMIT ?""",
                    (VerdictOutcome.FAIL.value, limit),
                ).fetchall()
            return [self._row_to_verdict(r) for r in rows]
        finally:
            conn.close()

    def trend(
        self,
        module_path: str,
        dimension: str,
        n: int = 10,
    ) -> list[dict[str, Any]]:
        """Get score trend for a module+dimension over recent evaluations.

        Returns list of {score, outcome, adg_digest, created_at} dicts,
        ordered oldest to newest.
        """
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT score, outcome, adg_digest, created_at
                   FROM verdicts
                   WHERE target = ? AND dimension = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (module_path, dimension, n),
            ).fetchall()
            return [
                {
                    "score": r["score"],
                    "outcome": r["outcome"],
                    "adg_digest": r["adg_digest"],
                    "created_at": r["created_at"],
                }
                for r in reversed(rows)
            ]
        finally:
            conn.close()

    def regressions(
        self,
        current_digest: str,
        previous_digest: str,
    ) -> list[dict[str, Any]]:
        """Find regressions between two ADG digests.

        Returns modules/dimensions where score decreased.
        """
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT
                     c.target, c.dimension, c.rubric_id,
                     c.score AS current_score, c.outcome AS current_outcome,
                     p.score AS previous_score, p.outcome AS previous_outcome,
                     (c.score - p.score) AS delta
                   FROM verdicts c
                   JOIN verdicts p
                     ON c.target = p.target
                     AND c.dimension = p.dimension
                     AND c.rubric_id = p.rubric_id
                   WHERE c.adg_digest = ?
                     AND p.adg_digest = ?
                     AND c.score < p.score
                   ORDER BY delta ASC""",
                (current_digest, previous_digest),
            ).fetchall()
            return [
                {
                    "target": r["target"],
                    "dimension": r["dimension"],
                    "rubric_id": r["rubric_id"],
                    "current_score": r["current_score"],
                    "previous_score": r["previous_score"],
                    "delta": round(r["delta"], 4),
                    "current_outcome": r["current_outcome"],
                    "previous_outcome": r["previous_outcome"],
                }
                for r in rows
            ]
        finally:
            conn.close()

    def stats(self) -> dict[str, Any]:
        """Get summary statistics for the verdict store."""
        conn = self._connect()
        try:
            total = conn.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
            by_outcome = {
                r[0]: r[1]
                for r in conn.execute(
                    "SELECT outcome, COUNT(*) FROM verdicts GROUP BY outcome",
                ).fetchall()
            }
            by_dimension = {
                r[0]: r[1]
                for r in conn.execute(
                    "SELECT dimension, COUNT(*) FROM verdicts GROUP BY dimension",
                ).fetchall()
            }
            distinct_targets = conn.execute(
                "SELECT COUNT(DISTINCT target) FROM verdicts",
            ).fetchone()[0]
            distinct_digests = conn.execute(
                "SELECT COUNT(DISTINCT adg_digest) FROM verdicts",
            ).fetchone()[0]

            return {
                "total_verdicts": total,
                "by_outcome": dict(by_outcome),
                "by_dimension": dict(by_dimension),
                "distinct_targets": distinct_targets,
                "distinct_digests": distinct_digests,
                "db_path": str(self._db_path),
            }
        finally:
            conn.close()


__all__ = ["VerdictStore"]

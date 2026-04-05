"""L4G CompletenessSnapshot - Context Health/Support Domain

Implements spec-compliant CompletenessSnapshot (L4G) from Agentic Retrieval Models v9:
- DOM: Context Health/Support
- KEY: trace_id/snap_hash
- DAT: [18] ContextComp
- MEC: Capture ContextCompScore, Log missing_signals, Feed CmpRAGProposer

Provides snapshot storage for completeness metrics with:
- Context completeness scoring
- Missing signal tracking
- Meta-learning feedback integration
- Temporal completeness analysis
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
    _emit_writes_learning_snapshot,
)

Logger = logging.getLogger(__name__)


@dataclass
class ContextCompletenessMetrics:
    """Context completeness metrics data contract [18]."""
    # Core completeness score (0-1)
    context_completeness_score: float = 0.0

    # Component scores
    coverage_score: float = 0.0  # Query term coverage
    diversity_score: float = 0.0  # Source diversity
    freshness_score: float = 0.0  # Temporal freshness
    authority_score: float = 0.0  # Source authority

    # Missing signals for meta-learning
    missing_signals: list[str] = field(default_factory=list)

    # Diagnostic info
    query_terms_covered: int = 0
    query_terms_total: int = 0
    sources_retrieved: int = 0
    sources_unique: int = 0

    # Thresholds for triggers
    completeness_threshold: float = 0.5
    coverage_threshold: float = 0.7


@dataclass
class CompletenessSnapshot:
    """Completeness snapshot for a retrieval context."""
    snap_id: str  # trace_id + hash
    trace_id: str
    query: str
    query_hash: str

    # Metrics
    metrics: ContextCompletenessMetrics

    # Context summary
    retrieved_contexts: list[dict[str, Any]]  # Chunk summaries
    context_count: int = 0

    # Triggers for Pipeline D
    triggered_actions: list[str] = field(default_factory=list)

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retrieval_config: dict[str, Any] = field(default_factory=dict)

    # Provenance
    session_id: str = ""
    user_id: str = ""


class CompletenessSnapshotRegistry:
    """L4G CompletenessSnapshotRegistry - Context Health Domain.

    Stores completeness snapshots with:
    - Context completeness scoring
    - Missing signal tracking
    - Meta-learning feedback emission
    - CompletenessRAGProposer feeding
    """

    def __init__(self, db_path: str = "artifacts/l4g_completeness.sqlite"):
        """Initialize CompletenessSnapshotRegistry.

        Args:
            db_path: SQLite database path
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completeness_snapshots (
                snap_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                query TEXT,
                query_hash TEXT,
                context_completeness_score REAL DEFAULT 0.0,
                coverage_score REAL DEFAULT 0.0,
                diversity_score REAL DEFAULT 0.0,
                freshness_score REAL DEFAULT 0.0,
                authority_score REAL DEFAULT 0.0,
                missing_signals TEXT,  -- JSON array
                query_terms_covered INTEGER DEFAULT 0,
                query_terms_total INTEGER DEFAULT 0,
                sources_retrieved INTEGER DEFAULT 0,
                sources_unique INTEGER DEFAULT 0,
                completeness_threshold REAL DEFAULT 0.5,
                coverage_threshold REAL DEFAULT 0.7,
                retrieved_contexts TEXT,  -- JSON
                context_count INTEGER DEFAULT 0,
                triggered_actions TEXT,  -- JSON array
                timestamp TEXT,
                retrieval_config TEXT,  -- JSON
                session_id TEXT,
                user_id TEXT,
                FOREIGN KEY (trace_id) REFERENCES evaluation_runs (trace_id)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trace_id_snap ON completeness_snapshots(trace_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp_snap ON completeness_snapshots(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_completeness_score ON completeness_snapshots(context_completeness_score)
        """)

        conn.commit()
        conn.close()

        Logger.info(f"Initialized CompletenessSnapshotRegistry at {self.db_path}")

    def compute_completeness(
        self,
        query: str,
        retrieved_contexts: list[dict[str, Any]],
        query_terms: list[str] | None = None,
    ) -> ContextCompletenessMetrics:
        """Compute context completeness metrics.

        Args:
            query: Original query
            retrieved_contexts: Retrieved contexts with metadata
            query_terms: Pre-extracted query terms

        Returns:
            ContextCompletenessMetrics
        """
        if query_terms is None:
            query_terms = query.lower().split()

        query_terms_set = set(query_terms)

        # Coverage: % of query terms found in contexts
        covered_terms = set()
        for ctx in retrieved_contexts:
            ctx_text = ctx.get("content", "").lower()
            for term in query_terms_set:
                if term in ctx_text:
                    covered_terms.add(term)

        coverage_score = len(covered_terms) / len(query_terms_set) if query_terms_set else 0.0

        # Diversity: unique sources / total sources
        sources = [ctx.get("source_file", ctx.get("doc_id", "unknown")) for ctx in retrieved_contexts]
        unique_sources = len(set(sources))
        total_sources = len(sources)
        diversity_score = unique_sources / total_sources if total_sources > 0 else 0.0

        # Freshness: temporal decay (simplified)
        freshness_score = 1.0  # Default fresh

        # Authority: source quality (simplified)
        authority_score = 1.0  # Default authoritative

        # Combined completeness score
        # Weight: coverage 50%, diversity 25%, freshness 15%, authority 10%
        context_completeness_score = (
            coverage_score * 0.5 +
            diversity_score * 0.25 +
            freshness_score * 0.15 +
            authority_score * 0.10
        )

        # Determine missing signals
        missing_signals = []

        if coverage_score < 0.7:
            missing_signals.append("low_coverage")

        if diversity_score < 0.5:
            missing_signals.append("low_diversity")

        if context_completeness_score < 0.5:
            missing_signals.append("low_completeness")

        return ContextCompletenessMetrics(
            context_completeness_score=context_completeness_score,
            coverage_score=coverage_score,
            diversity_score=diversity_score,
            freshness_score=freshness_score,
            authority_score=authority_score,
            missing_signals=missing_signals,
            query_terms_covered=len(covered_terms),
            query_terms_total=len(query_terms_set),
            sources_retrieved=total_sources,
            sources_unique=unique_sources,
        )

    def capture_snapshot(
        self,
        trace_id: str,
        query: str,
        retrieved_contexts: list[dict[str, Any]],
        retrieval_config: dict[str, Any] | None = None,
        session_id: str = "",
        user_id: str = "",
    ) -> CompletenessSnapshot:
        """Capture a completeness snapshot.

        Args:
            trace_id: Execution trace ID
            query: Original query
            retrieved_contexts: Retrieved context chunks
            retrieval_config: Configuration used for retrieval
            session_id: Session identifier
            user_id: User identifier

        Returns:
            CompletenessSnapshot with computed metrics
        """
        _trace_id = f"l4g_snap_{trace_id[:16]}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "CompletenessSnapshotRegistry.capture_snapshot"
        )

        # Generate IDs
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        snap_id = f"{trace_id}_{query_hash}"

        # Compute metrics
        metrics = self.compute_completeness(query, retrieved_contexts)

        # Determine triggered actions
        triggered_actions = []

        if metrics.context_completeness_score < metrics.completeness_threshold:
            triggered_actions.append("Depth++")
            _emit_writes_learning_snapshot(
                _trace_id, "completeness", metrics.context_completeness_score
            )

        if "low_diversity" in metrics.missing_signals:
            triggered_actions.append("Enrichment+")

        if coverage_score := metrics.coverage_score < metrics.coverage_threshold:
            triggered_actions.append("LexicalBoost")

        snapshot = CompletenessSnapshot(
            snap_id=snap_id,
            trace_id=trace_id,
            query=query,
            query_hash=query_hash,
            metrics=metrics,
            retrieved_contexts=retrieved_contexts,
            context_count=len(retrieved_contexts),
            triggered_actions=triggered_actions,
            timestamp=datetime.utcnow().isoformat(),
            retrieval_config=retrieval_config or {},
            session_id=session_id,
            user_id=user_id,
        )

        # Store snapshot
        self._store_snapshot(snapshot)

        # Emit meta-learning signal
        if triggered_actions:
            _emit_feeds_meta_learning(
                _trace_id, "CompletenessSnapshotRegistry", json.dumps(triggered_actions)
            )

        Logger.info(
            f"Captured completeness snapshot: {snap_id[:32]}... "
            f"(score={metrics.context_completeness_score:.2f}, "
            f"triggers={triggered_actions})"
        )

        return snapshot

    def _store_snapshot(self, snapshot: CompletenessSnapshot) -> bool:
        """Store snapshot in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metrics = snapshot.metrics

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO completeness_snapshots (
                    snap_id, trace_id, query, query_hash,
                    context_completeness_score, coverage_score, diversity_score,
                    freshness_score, authority_score, missing_signals,
                    query_terms_covered, query_terms_total,
                    sources_retrieved, sources_unique,
                    completeness_threshold, coverage_threshold,
                    retrieved_contexts, context_count, triggered_actions,
                    timestamp, retrieval_config, session_id, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.snap_id,
                snapshot.trace_id,
                snapshot.query,
                snapshot.query_hash,
                metrics.context_completeness_score,
                metrics.coverage_score,
                metrics.diversity_score,
                metrics.freshness_score,
                metrics.authority_score,
                json.dumps(metrics.missing_signals),
                metrics.query_terms_covered,
                metrics.query_terms_total,
                metrics.sources_retrieved,
                metrics.sources_unique,
                metrics.completeness_threshold,
                metrics.coverage_threshold,
                json.dumps(snapshot.retrieved_contexts),
                snapshot.context_count,
                json.dumps(snapshot.triggered_actions),
                snapshot.timestamp,
                json.dumps(snapshot.retrieval_config),
                snapshot.session_id,
                snapshot.user_id,
            ))

            conn.commit()
            return True

        except Exception as e:
            Logger.error(f"Failed to store snapshot: {e}")
            return False
        finally:
            conn.close()

    def get_snapshot(self, snap_id: str) -> CompletenessSnapshot | None:
        """Retrieve snapshot by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM completeness_snapshots WHERE snap_id = ?
            """, (snap_id,))

            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_snapshot(row, cursor)

        finally:
            conn.close()

    def get_snapshots_by_trace(self, trace_id: str) -> list[CompletenessSnapshot]:
        """Get all snapshots for a trace."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM completeness_snapshots WHERE trace_id = ?
            """, (trace_id,))

            rows = cursor.fetchall()
            return [self._row_to_snapshot(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_low_completeness_snapshots(
        self,
        threshold: float = 0.5,
        since: str | None = None,
    ) -> list[CompletenessSnapshot]:
        """Get snapshots with low completeness scores.

        Args:
            threshold: Completeness threshold
            since: ISO timestamp to filter from

        Returns:
            List of low completeness snapshots
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if since:
                cursor.execute("""
                    SELECT * FROM completeness_snapshots
                    WHERE context_completeness_score < ? AND timestamp >= ?
                    ORDER BY context_completeness_score ASC
                """, (threshold, since))
            else:
                cursor.execute("""
                    SELECT * FROM completeness_snapshots
                    WHERE context_completeness_score < ?
                    ORDER BY context_completeness_score ASC
                """, (threshold,))

            rows = cursor.fetchall()
            return [self._row_to_snapshot(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_aggregated_completeness(
        self,
        since: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated completeness metrics.

        Args:
            since: ISO timestamp to filter from

        Returns:
            Aggregated metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    AVG(context_completeness_score),
                    AVG(coverage_score),
                    AVG(diversity_score),
                    COUNT(*)
                FROM completeness_snapshots
            """
            params = []

            if since:
                query += " WHERE timestamp >= ?"
                params.append(since)

            cursor.execute(query, params)
            row = cursor.fetchone()

            # Count low completeness snapshots
            low_query = "SELECT COUNT(*) FROM completeness_snapshots WHERE context_completeness_score < 0.5"
            if since:
                low_query += " AND timestamp >= ?"

            cursor.execute(low_query, params)
            low_count = cursor.fetchone()[0]

            # Get trigger distribution
            cursor.execute("""
                SELECT triggered_actions FROM completeness_snapshots
                WHERE triggered_actions IS NOT NULL AND triggered_actions != '[]'
            """)

            trigger_counts = {}
            for (triggers_json,) in cursor.fetchall():
                try:
                    triggers = json.loads(triggers_json)
                    for trigger in triggers:
                        trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
                except:
                    pass

            return {
                "avg_completeness_score": row[0] or 0.0,
                "avg_coverage_score": row[1] or 0.0,
                "avg_diversity_score": row[2] or 0.0,
                "total_snapshots": row[3] or 0,
                "low_completeness_count": low_count,
                "trigger_distribution": trigger_counts,
            }

        finally:
            conn.close()

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        return self.get_aggregated_completeness()

    def _row_to_snapshot(
        self,
        row: tuple,
        cursor: sqlite3.Cursor,
    ) -> CompletenessSnapshot:
        """Convert database row to CompletenessSnapshot."""
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))

        metrics = ContextCompletenessMetrics(
            context_completeness_score=row_dict["context_completeness_score"],
            coverage_score=row_dict["coverage_score"],
            diversity_score=row_dict["diversity_score"],
            freshness_score=row_dict["freshness_score"],
            authority_score=row_dict["authority_score"],
            missing_signals=json.loads(row_dict["missing_signals"] or "[]"),
            query_terms_covered=row_dict["query_terms_covered"],
            query_terms_total=row_dict["query_terms_total"],
            sources_retrieved=row_dict["sources_retrieved"],
            sources_unique=row_dict["sources_unique"],
            completeness_threshold=row_dict["completeness_threshold"],
            coverage_threshold=row_dict["coverage_threshold"],
        )

        return CompletenessSnapshot(
            snap_id=row_dict["snap_id"],
            trace_id=row_dict["trace_id"],
            query=row_dict["query"],
            query_hash=row_dict["query_hash"],
            metrics=metrics,
            retrieved_contexts=json.loads(row_dict["retrieved_contexts"] or "[]"),
            context_count=row_dict["context_count"],
            triggered_actions=json.loads(row_dict["triggered_actions"] or "[]"),
            timestamp=row_dict["timestamp"],
            retrieval_config=json.loads(row_dict["retrieval_config"] or "{}"),
            session_id=row_dict["session_id"] or "",
            user_id=row_dict["user_id"] or "",
        )


# Global instance
_global_snapshot_registry: CompletenessSnapshotRegistry | None = None


def get_global_snapshot_registry() -> CompletenessSnapshotRegistry:
    """Get or create global snapshot registry."""
    global _global_snapshot_registry
    if _global_snapshot_registry is None:
        _global_snapshot_registry = CompletenessSnapshotRegistry()
    return _global_snapshot_registry


def capture_completeness_snapshot(
    trace_id: str,
    query: str,
    retrieved_contexts: list[dict[str, Any]],
) -> CompletenessSnapshot:
    """Convenience function to capture snapshot."""
    return get_global_snapshot_registry().capture_snapshot(
        trace_id, query, retrieved_contexts
    )

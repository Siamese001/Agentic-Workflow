"""L4F RetrievalEval Registry - Execution Quality Domain

Implements spec-compliant RetrievalEval (L4F) from Agentic Retrieval Models v9:
- DOM: Execution Quality
- KEY: trace_id/query_hash
- DAT: [19] SupportAnswerCheck
- MEC: Log Precision/Recall/MRR, Store NDCG, F1-Groundedness, Emit Shadow signals

Provides persistent storage for retrieval evaluation metrics with:
- SQLite backend for metrics
- Shadow/Replay mode support
- NDCG, MRR, Precision@K, Recall@K tracking
- F1-Groundedness computation
- Signal emission for meta-learning
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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class RetrievalEvaluation:
    """Retrieval evaluation data contract [19]."""
    eval_id: str  # trace_id + query_hash
    trace_id: str
    query_hash: str
    query_text: str

    # Retrieval context
    retrieved_chunk_ids: list[str]
    relevant_chunk_ids: list[str]  # Ground truth

    # Metrics
    precision_at_k: dict[int, float] = field(default_factory=dict)  # Precision@1, @5, @10
    recall_at_k: dict[int, float] = field(default_factory=dict)  # Recall@1, @5, @10
    mrr: float = 0.0  # Mean Reciprocal Rank
    ndcg: float = 0.0  # Normalized Discounted Cumulative Gain
    f1_groundedness: float = 0.0  # Support score

    # Answer quality (if answer generated)
    generated_answer: str = ""
    answer_supported: bool = True
    support_score: float = 0.0

    # Evaluation mode
    eval_mode: str = "shadow"  # shadow, replay, live

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retrieval_config: dict[str, Any] = field(default_factory=dict)

    # Signals for meta-learning
    triggers: list[str] = field(default_factory=list)  # completeness, fragmentation, etc.


class RetrievalEvalRegistry:
    """L4F RetrievalEvalRegistry - Execution Quality Domain.

    Stores retrieval evaluation metrics with:
    - Shadow/Replay/Live mode tracking
    - NDCG, MRR, P@K, R@K computation
    - F1-Groundedness tracking
    - Meta-learning signal emission
    """

    def __init__(self, db_path: str = "artifacts/l4f_evaluations.sqlite"):
        """Initialize RetrievalEvalRegistry.

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
            CREATE TABLE IF NOT EXISTS retrieval_evaluations (
                eval_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                query_hash TEXT NOT NULL,
                query_text TEXT,
                retrieved_chunk_ids TEXT,  -- JSON array
                relevant_chunk_ids TEXT,  -- JSON array
                precision_at_k TEXT,  -- JSON dict
                recall_at_k TEXT,  -- JSON dict
                mrr REAL DEFAULT 0.0,
                ndcg REAL DEFAULT 0.0,
                f1_groundedness REAL DEFAULT 0.0,
                generated_answer TEXT,
                answer_supported INTEGER DEFAULT 1,
                support_score REAL DEFAULT 0.0,
                eval_mode TEXT DEFAULT 'shadow',
                timestamp TEXT,
                retrieval_config TEXT,  -- JSON
                triggers TEXT,  -- JSON array
                FOREIGN KEY (trace_id) REFERENCES evaluation_runs (trace_id)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trace_id ON retrieval_evaluations(trace_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON retrieval_evaluations(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_eval_mode ON retrieval_evaluations(eval_mode)
        """)

        conn.commit()
        conn.close()

        Logger.info(f"Initialized RetrievalEvalRegistry at {self.db_path}")

    def compute_metrics(
        self,
        retrieved: list[str],
        relevant: list[str],
        k_values: list[int] = None,
    ) -> dict[str, Any]:
        """Compute retrieval metrics.

        Args:
            retrieved: List of retrieved chunk IDs (ordered)
            relevant: List of relevant chunk IDs (ground truth)
            k_values: K values for P@K and R@K

        Returns:
            Dict with computed metrics
        """
        if k_values is None:
            k_values = [1, 5, 10]

        relevant_set = set(relevant)

        # Precision@K and Recall@K
        precision_at_k = {}
        recall_at_k = {}

        for k in k_values:
            if k > len(retrieved):
                k = len(retrieved)

            retrieved_k = set(retrieved[:k])
            relevant_in_k = len(retrieved_k & relevant_set)

            precision_at_k[k] = relevant_in_k / k if k > 0 else 0.0
            recall_at_k[k] = relevant_in_k / len(relevant_set) if relevant_set else 0.0

        # MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for rank, chunk_id in enumerate(retrieved, 1):
            if chunk_id in relevant_set:
                mrr = 1.0 / rank
                break

        # NDCG (Normalized Discounted Cumulative Gain)
        dcg = 0.0
        for rank, chunk_id in enumerate(retrieved, 1):
            if chunk_id in relevant_set:
                # Relevance is binary (1 if relevant, 0 if not)
                gain = 1.0
                dcg += gain / (1 + rank)

        # Ideal DCG (all relevant docs at top)
        ideal_dcg = sum(1.0 / (1 + rank) for rank in range(1, len(relevant) + 1))

        ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0.0

        return {
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "ndcg": ndcg,
        }

    def evaluate_retrieval(
        self,
        trace_id: str,
        query: str,
        retrieved_chunks: list[str],
        relevant_chunks: list[str],
        eval_mode: str = "shadow",
        retrieval_config: dict[str, Any] | None = None,
    ) -> RetrievalEvaluation:
        """Evaluate a retrieval and store results.

        Args:
            trace_id: Execution trace ID
            query: Query text
            retrieved_chunks: Retrieved chunk IDs
            relevant_chunks: Ground truth relevant chunk IDs
            eval_mode: Evaluation mode (shadow, replay, live)
            retrieval_config: Configuration used for retrieval

        Returns:
            RetrievalEvaluation with computed metrics
        """
        _trace_id = f"l4f_eval_{trace_id[:16]}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "RetrievalEvalRegistry.evaluate_retrieval"
        )

        # Generate eval_id
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        eval_id = f"{trace_id}_{query_hash}"

        # Compute metrics
        metrics = self.compute_metrics(retrieved_chunks, relevant_chunks)

        # Determine triggers for meta-learning
        triggers = []

        # Completeness trigger (NDCG < 0.5)
        if metrics["ndcg"] < 0.5:
            triggers.append("completeness")
            _emit_captures_evaluation_metric(_trace_id, "retrieval", "ndcg_low", metrics["ndcg"])

        # Fragmentation trigger (Precision drops significantly at higher K)
        p_at_1 = metrics["precision_at_k"].get(1, 0.0)
        p_at_10 = metrics["precision_at_k"].get(10, 0.0)
        if p_at_1 > 0.8 and p_at_10 < 0.3:
            triggers.append("fragmentation")
            _emit_captures_evaluation_metric(_trace_id, "retrieval", "fragmentation_detected", p_at_1 - p_at_10)

        # Groundedness trigger (F1 will be computed later with answer)

        eval_result = RetrievalEvaluation(
            eval_id=eval_id,
            trace_id=trace_id,
            query_hash=query_hash,
            query_text=query,
            retrieved_chunk_ids=retrieved_chunks,
            relevant_chunk_ids=relevant_chunks,
            precision_at_k=metrics["precision_at_k"],
            recall_at_k=metrics["recall_at_k"],
            mrr=metrics["mrr"],
            ndcg=metrics["ndcg"],
            eval_mode=eval_mode,
            retrieval_config=retrieval_config or {},
            triggers=triggers,
            timestamp=datetime.utcnow().isoformat(),
        )

        # Store
        self._store_evaluation(eval_result)

        # Emit meta-learning signal
        if triggers:
            _emit_feeds_meta_learning(
                _trace_id, "RetrievalEvalRegistry", json.dumps(triggers)
            )

        Logger.info(f"Evaluated retrieval: {eval_id[:32]}... (NDCG={metrics['ndcg']:.2f})")

        return eval_result

    def evaluate_answer(
        self,
        eval_id: str,
        generated_answer: str,
        support_score: float,
    ) -> bool:
        """Evaluate answer groundedness and update evaluation.

        Args:
            eval_id: Evaluation ID
            generated_answer: Generated answer text
            support_score: Support score (0-1)

        Returns:
            True if updated successfully
        """
        _trace_id = f"l4f_answer_{eval_id[:16]}"

        f1_groundedness = support_score  # F1 proxy
        answer_supported = support_score >= 0.5

        # Check for groundedness trigger
        triggers = []
        if f1_groundedness < 0.5:
            triggers.append("groundedness")
            _emit_captures_evaluation_metric(
                _trace_id, "retrieval", "f1_groundedness_low", f1_groundedness
            )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update evaluation with answer metrics
            cursor.execute("""
                UPDATE retrieval_evaluations SET
                    generated_answer = ?,
                    support_score = ?,
                    f1_groundedness = ?,
                    answer_supported = ?,
                    triggers = json_insert(triggers, '$', ?)
                WHERE eval_id = ?
            """, (
                generated_answer,
                support_score,
                f1_groundedness,
                1 if answer_supported else 0,
                json.dumps(triggers),
                eval_id,
            ))

            conn.commit()

            if triggers:
                _emit_feeds_meta_learning(
                    _trace_id, "RetrievalEvalRegistry", json.dumps(triggers)
                )

            Logger.info(f"Evaluated answer: {eval_id[:32]}... (F1={f1_groundedness:.2f})")
            return True

        except Exception as e:
            Logger.error(f"Failed to evaluate answer: {e}")
            return False
        finally:
            conn.close()

    def _store_evaluation(self, evaluation: RetrievalEvaluation) -> bool:
        """Store evaluation in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO retrieval_evaluations (
                    eval_id, trace_id, query_hash, query_text,
                    retrieved_chunk_ids, relevant_chunk_ids,
                    precision_at_k, recall_at_k, mrr, ndcg, f1_groundedness,
                    generated_answer, answer_supported, support_score,
                    eval_mode, timestamp, retrieval_config, triggers
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evaluation.eval_id,
                evaluation.trace_id,
                evaluation.query_hash,
                evaluation.query_text,
                json.dumps(evaluation.retrieved_chunk_ids),
                json.dumps(evaluation.relevant_chunk_ids),
                json.dumps(evaluation.precision_at_k),
                json.dumps(evaluation.recall_at_k),
                evaluation.mrr,
                evaluation.ndcg,
                evaluation.f1_groundedness,
                evaluation.generated_answer,
                1 if evaluation.answer_supported else 0,
                evaluation.support_score,
                evaluation.eval_mode,
                evaluation.timestamp,
                json.dumps(evaluation.retrieval_config),
                json.dumps(evaluation.triggers),
            ))

            conn.commit()
            return True

        except Exception as e:
            Logger.error(f"Failed to store evaluation: {e}")
            return False
        finally:
            conn.close()

    def get_evaluation(self, eval_id: str) -> RetrievalEvaluation | None:
        """Retrieve evaluation by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM retrieval_evaluations WHERE eval_id = ?
            """, (eval_id,))

            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_evaluation(row, cursor)

        finally:
            conn.close()

    def get_evaluations_by_trace(self, trace_id: str) -> list[RetrievalEvaluation]:
        """Get all evaluations for a trace."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM retrieval_evaluations WHERE trace_id = ?
            """, (trace_id,))

            rows = cursor.fetchall()
            return [self._row_to_evaluation(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_aggregated_metrics(
        self,
        since: str | None = None,
        eval_mode: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated metrics over time.

        Args:
            since: ISO timestamp to filter from
            eval_mode: Filter by evaluation mode

        Returns:
            Aggregated metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = "SELECT AVG(mrr), AVG(ndcg), AVG(f1_groundedness), COUNT(*) FROM retrieval_evaluations"
            params = []

            conditions = []
            if since:
                conditions.append("timestamp >= ?")
                params.append(since)
            if eval_mode:
                conditions.append("eval_mode = ?")
                params.append(eval_mode)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            row = cursor.fetchone()

            # Get trigger counts
            cursor.execute("""
                SELECT triggers FROM retrieval_evaluations
                WHERE triggers IS NOT NULL AND triggers != '[]'
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
                "avg_mrr": row[0] or 0.0,
                "avg_ndcg": row[1] or 0.0,
                "avg_f1_groundedness": row[2] or 0.0,
                "total_evaluations": row[3] or 0,
                "trigger_distribution": trigger_counts,
            }

        finally:
            conn.close()

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        return self.get_aggregated_metrics()

    def _row_to_evaluation(
        self,
        row: tuple,
        cursor: sqlite3.Cursor,
    ) -> RetrievalEvaluation:
        """Convert database row to RetrievalEvaluation."""
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))

        return RetrievalEvaluation(
            eval_id=row_dict["eval_id"],
            trace_id=row_dict["trace_id"],
            query_hash=row_dict["query_hash"],
            query_text=row_dict["query_text"],
            retrieved_chunk_ids=json.loads(row_dict["retrieved_chunk_ids"] or "[]"),
            relevant_chunk_ids=json.loads(row_dict["relevant_chunk_ids"] or "[]"),
            precision_at_k=json.loads(row_dict["precision_at_k"] or "{}"),
            recall_at_k=json.loads(row_dict["recall_at_k"] or "{}"),
            mrr=row_dict["mrr"],
            ndcg=row_dict["ndcg"],
            f1_groundedness=row_dict["f1_groundedness"],
            generated_answer=row_dict["generated_answer"] or "",
            answer_supported=bool(row_dict["answer_supported"]),
            support_score=row_dict["support_score"],
            eval_mode=row_dict["eval_mode"],
            timestamp=row_dict["timestamp"],
            retrieval_config=json.loads(row_dict["retrieval_config"] or "{}"),
            triggers=json.loads(row_dict["triggers"] or "[]"),
        )


# Global instance
_global_eval_registry: RetrievalEvalRegistry | None = None


def get_global_eval_registry() -> RetrievalEvalRegistry:
    """Get or create global eval registry."""
    global _global_eval_registry
    if _global_eval_registry is None:
        _global_eval_registry = RetrievalEvalRegistry()
    return _global_eval_registry

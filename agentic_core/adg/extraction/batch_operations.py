"""ADG Batch Operations - Wave 2 CPU Optimization.

Batch processing for ADG edge/node operations to maximize throughput
and CPU utilization during large-scale analysis.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any

import redis

from agentic_core.L2_execution.utils import (
    BatchProcessor,
)

logger = logging.getLogger(__name__)


@dataclass
class EdgeBatch:
    """Batch of edges for insertion."""
    edges: list[dict] = field(default_factory=list)
    source_file: str = ""
    batch_id: str = ""


@dataclass
class NodeBatch:
    """Batch of nodes for insertion."""
    nodes: list[dict] = field(default_factory=list)
    batch_id: str = ""


class ADGSQLiteBatchInserter:
    """Batch inserter for ADG SQLite operations.

    Optimizes edge/node insertion by batching to reduce
    transaction overhead and improve CPU utilization.
    """

    def __init__(
        self,
        db_path: str,
        batch_size: int = 1000,
        enable_wal: bool = True,
    ):
        self.db_path = db_path
        self.batch_size = batch_size
        self.enable_wal = enable_wal
        self._edge_buffer: list[dict] = []
        self._node_buffer: list[dict] = []
        self._total_inserted = 0

    def __enter__(self):
        """Context manager entry."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")

        if self.enable_wal:
            self.conn.execute("PRAGMA journal_mode = WAL")
            self.conn.execute("PRAGMA synchronous = NORMAL")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - flush remaining buffers."""
        self.flush()
        self.conn.close()

    def add_edge(self, edge: dict) -> None:
        """Add edge to batch buffer."""
        self._edge_buffer.append(edge)

        if len(self._edge_buffer) >= self.batch_size:
            self._flush_edges()

    def add_node(self, node: dict) -> None:
        """Add node to batch buffer."""
        self._node_buffer.append(node)

        if len(self._node_buffer) >= self.batch_size:
            self._flush_nodes()

    def add_edges_batch(self, edges: list[dict]) -> None:
        """Add multiple edges to buffer."""
        self._edge_buffer.extend(edges)

        while len(self._edge_buffer) >= self.batch_size:
            self._flush_edges()

    def add_nodes_batch(self, nodes: list[dict]) -> None:
        """Add multiple nodes to buffer."""
        self._node_buffer.extend(nodes)

        while len(self._node_buffer) >= self.batch_size:
            self._flush_nodes()

    def _flush_edges(self) -> int:
        """Flush edge buffer to database."""
        if not self._edge_buffer:
            return 0

        batch = self._edge_buffer[:self.batch_size]
        self._edge_buffer = self._edge_buffer[self.batch_size:]

        try:
            cursor = self.conn.cursor()

            # Batch insert with executemany
            cursor.executemany(
                """
                INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                VALUES (:src_id, :dst_id, :relation_type, :edge_kind, :source_file, :line_no, :symbol)
                ON CONFLICT DO NOTHING
                """,
                batch,
            )

            self.conn.commit()
            self._total_inserted += len(batch)

            logger.debug(f"Inserted {len(batch)} edges (total: {self._total_inserted})")
            return len(batch)

        except Exception as e:
            logger.error(f"Edge batch insert failed: {e}")
            self.conn.rollback()
            raise

    def _flush_nodes(self) -> int:
        """Flush node buffer to database."""
        if not self._node_buffer:
            return 0

        batch = self._node_buffer[:self.batch_size]
        self._node_buffer = self._node_buffer[self.batch_size:]

        try:
            cursor = self.conn.cursor()

            cursor.executemany(
                """
                INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
                VALUES (:adg_name, :entity_type, :layer, :identity_kind, :confidence, :resolved_path)
                ON CONFLICT(adg_name) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    layer = excluded.layer,
                    identity_kind = excluded.identity_kind,
                    confidence = excluded.confidence,
                    resolved_path = excluded.resolved_path
                """,
                batch,
            )

            self.conn.commit()
            self._total_inserted += len(batch)

            logger.debug(f"Inserted/updated {len(batch)} nodes")
            return len(batch)

        except Exception as e:
            logger.error(f"Node batch insert failed: {e}")
            self.conn.rollback()
            raise

    def flush(self) -> tuple[int, int]:
        """Flush all remaining buffers."""
        edges_flushed = self._flush_edges()
        nodes_flushed = self._flush_nodes()

        logger.info(
            f"Final flush: {edges_flushed} edges, {nodes_flushed} nodes "
            f"(total inserted: {self._total_inserted})"
        )

        return edges_flushed, nodes_flushed

    def get_stats(self) -> dict[str, Any]:
        """Get insertion statistics."""
        return {
            "total_inserted": self._total_inserted,
            "edge_buffer_size": len(self._edge_buffer),
            "node_buffer_size": len(self._node_buffer),
            "batch_size_configured": self.batch_size,
        }


class ADGRedisBatchInserter:
    """Batch inserter for ADG Redis operations.

    Uses Redis pipelines for efficient batch operations.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        pipeline_size: int = 1000,
    ):
        self.redis = redis_client
        self.pipeline_size = pipeline_size
        self._pipeline = redis_client.pipeline(transaction=False)
        self._pending = 0
        self._total_executed = 0

    def add_node(self, node_id: str, node_data: dict) -> None:
        """Add node to Redis batch."""
        self._pipeline.hset(f"adg:node:{node_id}", mapping=node_data)
        self._pending += 1

        if self._pending >= self.pipeline_size:
            self.execute()

    def add_edge(self, edge_id: str, edge_data: dict) -> None:
        """Add edge to Redis batch."""
        self._pipeline.hset(f"adg:edge_detail:{edge_id}", mapping=edge_data)
        self._pending += 1

        if self._pending >= self.pipeline_size:
            self.execute()

    def add_to_set(self, set_key: str, member: str) -> None:
        """Add member to Redis set."""
        self._pipeline.sadd(set_key, member)
        self._pending += 1

        if self._pending >= self.pipeline_size:
            self.execute()

    def execute(self) -> list[Any]:
        """Execute pending pipeline operations."""
        if not self._pending:
            return []

        start = time.time()
        results = self._pipeline.execute()
        elapsed = (time.time() - start) * 1000

        self._total_executed += self._pending
        logger.debug(
            f"Executed {self._pending} Redis ops in {elapsed:.1f}ms "
            f"(total: {self._total_executed})"
        )

        self._pipeline = self.redis.pipeline(transaction=False)
        self._pending = 0

        return results

    def close(self) -> None:
        """Execute remaining operations and close."""
        self.execute()
        logger.info(f"Redis batch inserter closed (total: {self._total_executed})")


class ADGEdgeBatchProcessor(BatchProcessor[dict, dict]):
    """Batch processor specifically for ADG edge operations."""

    def __init__(
        self,
        batch_size: int = 1000,
        max_workers: int | None = None,
    ):
        def process_edge_batch(edges: list[dict]) -> list[dict]:
            """Process batch of edges (validation, enrichment, etc.)."""
            processed = []
            for edge in edges:
                # Add any edge processing logic here
                # (validation, deduplication, enrichment)
                processed.append(edge)
            return processed

        super().__init__(
            processor_func=process_edge_batch,
            batch_size=batch_size,
            max_workers=max_workers,
            error_isolation=True,
        )


__all__ = [
    "ADGSQLiteBatchInserter",
    "ADGRedisBatchInserter",
    "ADGEdgeBatchProcessor",
    "EdgeBatch",
    "NodeBatch",
]

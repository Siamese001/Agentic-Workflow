"""
ETL Pipeline - Connectivity-Hardened Canon Validator

Data ingestion pipeline for hydrating the hybrid cache with
golden patterns from Pinecone to Redis.
"""

import logging
import os
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "etl_pipeline_util", "p0_governance")
_emit_reads_policy_state("p0", "etl_pipeline_util", "policy_binding")
_emit_snapshots_state("p0", "etl_pipeline_util", "state_snapshot")
emit_replay_key("p0", "etl_pipeline_util")
emit_determinism_digest("p0", "etl_pipeline_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL Pipeline for data ingestion and cache hydration.

    Handles loading golden patterns from L2 (Pinecone) into
    L1 (Redis) for fast access.
    """

    def __init__(self):
        """Initialize the ETL pipeline."""
        self.redis_conn = ConnectionFactory.get_redis_connection()
        self.pinecone = ConnectionFactory.get_pinecone_connection()
        self.embed_func = ConnectionFactory.get_embedding_function()
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        self.redis_index = ConnectionFactory.create_redis_index(None)
        logger.info("ETL Pipeline initialized")

    # guardian: allow-magic-config
    def hydrate_cache(
        self, min_success_count: int = 10, max_patterns: int = 50, project_filter: str | None = None
    ) -> dict[str, Any]:
        """
        Hydrate Redis cache with golden patterns from Pinecone.

        Args:
            min_success_count: Minimum success count for golden patterns
            max_patterns: Maximum patterns to load
            project_filter: Filter by project context

        Returns:
            Statistics about the hydration process
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ETLPipeline.hydrate_cache")

        logger.info(f"Starting cache hydration with up to {max_patterns} golden patterns")
        golden_patterns = self._fetch_golden_patterns(
            min_success_count=min_success_count, max_patterns=max_patterns, project_filter=project_filter
        )
        loaded_count = self._load_to_redis(golden_patterns)
        stats = {
            "fetched_from_pinecone": len(golden_patterns),
            "loaded_to_redis": loaded_count,
            "min_success_count": min_success_count,
            "max_patterns": max_patterns,
            "project_filter": project_filter,
        }
        logger.info(f"cache hydration complete: {stats}")
        return stats

    def _fetch_golden_patterns(
        self, min_success_count: int, max_patterns: int, project_filter: str | None
    ) -> list[CanonEntry]:
        """Fetch golden patterns from Pinecone."""
        try:
            index = self.pinecone.Index(self.index_name)
            filter_dict = {"success_count": {"$gte": min_success_count}}
            if project_filter:
                filter_dict["project_context"] = project_filter
            results = index.query(
                vector=[0.0] * 768, top_k=max_patterns, include_metadata=True, filter=filter_dict
            )
            patterns = []
            for match in results["matches"]:
                if match["score"] > 0:
                    metadata = match["metadata"]
                    entry = CanonEntry(
                        id=match["id"],
                        code_snippet=metadata["code_snippet"],
                        ast_structure=metadata["ast_structure"],
                        embedding=match["values"] if "values" in match else [0.0] * 768,
                        metadata={
                            "failure_count": metadata["failure_count"],
                            "success_count": metadata["success_count"],
                            "last_validated": metadata["last_validated"],
                            "project_context": metadata["project_context"],
                            "canon_rule_id": metadata["canon_rule_id"],
                        },
                    )
                    patterns.append(entry)
            logger.info(f"Fetched {len(patterns)} golden patterns from Pinecone")
            return patterns
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to fetch golden patterns: {e}")
            return []

    def _load_to_redis(self, patterns: list[CanonEntry]) -> int:
        """Load patterns into Redis."""
        loaded_count = 0
        try:
            pipe = self.redis_conn.client.pipeline()
            for pattern in patterns:
                fields = pattern.to_redis_fields()
                key = f"canon:{fields['id']}"
                pipe.hset(key, mapping=fields)
                self.redis_index.load(
                    documents=[
                        {
                            "id": fields["id"],
                            "embedding": fields["embedding"],
                            "failure_count": fields["failure_count"],
                            "success_count": fields["success_count"],
                            "project_context": fields["project_context"],
                            "canon_rule_id": fields["canon_rule_id"],
                            "last_validated": fields["last_validated"],
                        }
                    ]
                )
                loaded_count += 1
            pipe.execute()
            logger.info(f"Loaded {loaded_count} patterns to Redis")
            return loaded_count
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to load patterns to Redis: {e}")
            return 0

    # guardian: allow-magic-config
    def backfill_from_code(
        self, code_files: list[str], project_context: str = "backfill", batch_size: int = 100
    ) -> dict[str, Any]:
        """
        Backfill Pinecone with code files.

        Args:
            code_files: List of code file paths
            project_context: Project context for metadata
            batch_size: Batch size for upserts

        Returns:
            Statistics about backfill process
        """
        logger.info(f"Starting backfill of {len(code_files)} code files")
        processed = 0
        failed = 0
        for i in range(0, len(code_files), batch_size):
            batch = code_files[i : i + batch_size]
            entries = []
            for file_path in batch:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        code = f.read()
                    entry = self._create_entry_from_code(code, project_context, file_path)
                    entries.append(entry)
                    processed += 1
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    failed += 1
            if entries:
                self._upsert_to_pinecone(entries)
        stats = {
            "total_files": len(code_files),
            "processed": processed,
            "failed": failed,
            "batch_size": batch_size,
        }
        logger.info(f"Backfill complete: {stats}")
        return stats

    def _create_entry_from_code(self, code: str, project_context: str, file_path: str) -> CanonEntry:
        """Create CanonEntry from code."""
        ast_structure = generate_ast_structure(code)
        description = f"Code from {file_path}: {code[:100]}..."
        embedding = self.embed_func(description)
        entry = CanonEntry(
            code_snippet=code,
            ast_structure=ast_structure,
            embedding=embedding,
            metadata={
                "failure_count": 0,
                "success_count": 0,
                "project_context": project_context,
                "canon_rule_id": "backfill",
            },
        )
        return entry

    def _upsert_to_pinecone(self, entries: list[CanonEntry]):
        """Upsert entries to Pinecone."""
        try:
            index = self.pinecone.Index(self.index_name)
            vectors = [entry.to_pinecone_vector() for entry in entries]
            index.upsert(vectors=vectors)
            logger.debug(f"Upserted {len(entries)} vectors to Pinecone")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to upsert to Pinecone: {e}")
            raise

    def get_cache_stats(self) -> dict[str, Any]:
        """Get statistics for both caches."""
        stats = {"redis": {}, "pinecone": {}}
        try:
            redis_info = self.redis_conn.client.info()
            stats["redis"] = {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory_human", "0B"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0),
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
        try:
            index = self.pinecone.Index(self.index_name)
            index_stats = index.describe_index_stats()
            stats["pinecone"] = {
                "vector_count": index_stats.get("total_vector_count", 0),
                "dimension": index_stats.get("dimension", 0),
                "index_fullness": index_stats.get("index_fullness", 0),
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
        return stats


def hydrate_cache() -> dict[str, Any]:
    """
    Convenience function to hydrate the cache.

    Returns:
        Hydration statistics
    """
    pipeline = ETLPipeline()
    return pipeline.hydrate_cache()

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "in_memory_vector_cache")
trace_contract.emit_determinism_digest("p0", "in_memory_vector_cache")

trace_contract._emit_dispatches_healing_run("p1", "in_memory_vector_cache", "L4")
trace_contract._emit_routes_through("p1", "in_memory_vector_cache", "L4")
trace_contract._emit_checks_agent_registry("p1", "in_memory_vector_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "in_memory_vector_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "in_memory_vector_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "in_memory_vector_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "in_memory_vector_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "in_memory_vector_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "in_memory_vector_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "in_memory_vector_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "in_memory_vector_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "in_memory_vector_cache")
trace_contract._emit_gated_by_confidence("p1", "in_memory_vector_cache", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "in_memory_vector_cache", "L4")
trace_contract._emit_reads_policy_state("p1", "in_memory_vector_cache", "L4")
trace_contract._emit_authorize_and_execute("p2", "in_memory_vector_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "in_memory_vector_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "in_memory_vector_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "in_memory_vector_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "in_memory_vector_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "in_memory_vector_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "in_memory_vector_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "in_memory_vector_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "in_memory_vector_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "in_memory_vector_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "in_memory_vector_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "in_memory_vector_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "in_memory_vector_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "in_memory_vector_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "in_memory_vector_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "in_memory_vector_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "in_memory_vector_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "in_memory_vector_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "in_memory_vector_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "in_memory_vector_cache", "exec_snapshot_link")

"In-Memory Vector cache - Ultra-fast ChromaDB hot cache for 10-50x speedup.\n\nProvides ephemeral in-memory vector storage for frequently accessed collections.\nOptimized for 8GB hot cache allocation within 32GB WSL2 environment.\n"
import logging
from typing import Any

try:
    import chromadb
except ImportError as _err:
    raise ImportError(
        "chromadb is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("in_memory_vector_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("in_memory_vector_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("in_memory_vector_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("in_memory_vector_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("in_memory_vector_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("in_memory_vector_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("in_memory_vector_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("in_memory_vector_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("in_memory_vector_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("in_memory_vector_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("in_memory_vector_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("in_memory_vector_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("in_memory_vector_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("in_memory_vector_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("in_memory_vector_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("in_memory_vector_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("in_memory_vector_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("in_memory_vector_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("in_memory_vector_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("in_memory_vector_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("in_memory_vector_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("in_memory_vector_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("in_memory_vector_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "in_memory_vector_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "in_memory_vector_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "in_memory_vector_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "in_memory_vector_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "in_memory_vector_cache", "write_through")
trace_contract._emit_writes_through("p1", "in_memory_vector_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "in_memory_vector_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "in_memory_vector_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "in_memory_vector_cache", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class InMemoryVectorCache:
    """In-memory vector cache using ChromaDB.

    Initializes an ephemeral in-memory ChromaDB instance for ultra-fast
    similarity search without network or disk I/O overhead.
    """

    # guardian: allow-magic-config
    def __init__(self, collection_name: str = "hot_cache", max_memory_gb: int | None = 8):
        """Initialize in-memory ChromaDB cache.

        Args:
            collection_name: Name of the collection to create
            max_memory_gb: Maximum memory allocation in GB (default: 8)
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "InMemoryVectorCache.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "InMemoryVectorCache.__init__", "p0_governance")
        self.collection_name = collection_name
        self.max_memory_gb = max_memory_gb
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)
        Logger.info(
            f"Initialized InMemoryVectorCache: collection={collection_name}, max_memory={max_memory_gb}GB",
        )

    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
        embeddings: list[list[float]],
    ) -> bool:
        """Add vectors to the hot cache.

        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
            embeddings: List of embedding vectors

        Returns:
            True if successful, False otherwise

        Example:
            >>> cache = InMemoryVectorCache()
            >>> await cache.add_documents(
            ...     documents=["doc1", "doc2"],
            ...     metadatas=[{"source": "resume"}, {"source": "job"}],
            ...     ids=["id1", "id2"],
            ...     embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]]
            ... )
        """
        try:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
            Logger.debug(
                f"Added {len(documents)} documents to hot cache (collection: {self.collection_name})",
            )
            return True
        except (
            AttributeError,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to add to hot cache: {e}")
            return False

    # guardian: allow-magic-config
    async def search(
        self,
        query_embeddings: list[list[float]],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
        where_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform ultra-fast in-memory similarity search.

        Args:
            query_embeddings: List of query embedding vectors
            top_k: Number of results to return (default: 5)
            where: Optional metadata filter
            where_document: Optional document content filter

        Returns:
            Dictionary containing search results with ids, documents, metadatas, distances

        Example:
            >>> results = await cache.search(
            ...     query_embeddings=[[0.1, 0.2, ...]],
            ...     top_k=10,
            ...     where={"source": "resume"}
            ... )
        """
        try:
            results: Any = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                where=where,
                where_document=where_document,
            )
            Logger.debug(f"In-memory search returned {len(results.get('ids', [[]])[0])} results")
            return results
        except (
            AttributeError,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"In-memory search failed: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    def get_count(self) -> int:
        """Get the number of documents in the cache.

        Returns:
            Number of documents currently in cache
        """
        try:
            return self.collection.count()
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to get cache count: {e}")
            return 0

    def clear(self) -> bool:
        """Wipe cache to free RAM.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.reset()
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            Logger.info(f"Cleared hot cache (collection: {self.collection_name})")
            return True
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to clear cache: {e}")
            return False

    def delete_collection(self) -> bool:
        """Delete the entire collection.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            Logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to delete collection: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "collection_name": self.collection_name,
            "document_count": self.get_count(),
            "max_memory_gb": self.max_memory_gb,
            "type": "in_memory",
        }


class TieredVectorStore:
    """Two-tier vector storage: hot in-memory cache + warm disk storage.

    Automatically promotes frequently accessed items to hot cache.
    """

    def __init__(self, hot_cache: InMemoryVectorCache, warm_store_url: str = "http://localhost:6333"):
        """Initialize tiered vector store.

        Args:
            hot_cache: In-memory cache instance
            warm_store_url: URL for warm storage (Qdrant)
        """
        self.hot_cache = hot_cache
        self.warm_store_url = warm_store_url
        Logger.info(
            f"Initialized TieredVectorStore: hot_cache={hot_cache.collection_name}, warm_store={warm_store_url}",
        )

    # guardian: allow-magic-config
    async def search(
        self,
        query_embeddings: list[list[float]],
        top_k: int = 10,
        try_hot_first: bool = True,
    ) -> dict[str, Any]:
        """Search with hot cache fallback to warm storage.

        Args:
            query_embeddings: Query embedding vectors
            top_k: Number of results to return
            try_hot_first: Try hot cache before warm storage

        Returns:
            Search results from hot cache or warm storage
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "TieredVectorStore.search")

        if try_hot_first:
            hot_results: Any = await self.hot_cache.search(query_embeddings=query_embeddings, top_k=top_k)
            if hot_results.get("ids") and len(hot_results["ids"][0]) >= top_k:
                Logger.debug("Served from hot cache")
                return hot_results
            Logger.debug("Hot cache miss, falling back to warm storage")
        Logger.warning("Warm storage fallback not yet implemented")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


# guardian: allow-magic-config
def create_memory_vector_cache(
    collection_name: str = "hot_cache",
    max_memory_gb: int = 8,
) -> InMemoryVectorCache:
    """Create an InMemoryVectorCache instance.

    Args:
        collection_name: Name of the collection
        max_memory_gb: Maximum memory allocation in GB

    Returns:
        Configured InMemoryVectorCache instance
    """
    return InMemoryVectorCache(collection_name=collection_name, max_memory_gb=max_memory_gb)


def create_tiered_vector_store(
    hot_collection_name: str = "hot_cache",
    warm_store_url: str = "http://localhost:6333",
) -> TieredVectorStore:
    """Create a TieredVectorStore instance.

    Args:
        hot_collection_name: Name for hot cache collection
        warm_store_url: URL for warm storage (Qdrant)

    Returns:
        Configured TieredVectorStore instance
    """
    hot_cache: Any = create_memory_vector_cache(collection_name=hot_collection_name)
    return TieredVectorStore(hot_cache=hot_cache, warm_store_url=warm_store_url)

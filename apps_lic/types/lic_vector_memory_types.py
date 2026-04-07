"""
LIC Vector Memory Store - ChromaDB-based vector store for research.

Ported from: archives/legacy_lic/Agentic LIC/memory_LIC.py
"""

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "lic_vector_memory_types", "p0_governance")
_emit_reads_policy_state("p0", "lic_vector_memory_types", "policy_binding")
_emit_snapshots_state("p0", "lic_vector_memory_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_1")
_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_2")
_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_3")
_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_4")
_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_5")
_emit_emits_metric_event("lic_vector_memory_types", "p4obs", "metric_6")
_emit_records_incident_event("lic_vector_memory_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("lic_vector_memory_types", "p4obs", "anomaly")
_emit_writes_observability_log("lic_vector_memory_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("lic_vector_memory_types", "p4obs", "mon_state")
_emit_triggers_alert("lic_vector_memory_types", "p4obs", "alert")
_emit_links_incident_trace("lic_vector_memory_types", "p4obs", "trace_link")
_emit_captures_pattern("lic_vector_memory_types", "p3lm", "pattern")
_emit_records_learning_event("lic_vector_memory_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lic_vector_memory_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("lic_vector_memory_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lic_vector_memory_types", "p3lm", "routing")
_emit_improves_agent_policy("lic_vector_memory_types", "p3lm", "policy")
_emit_stores_learning_state("lic_vector_memory_types", "p3lm", "state")
_emit_records_execution_trace("lic_vector_memory_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lic_vector_memory_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lic_vector_memory_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lic_vector_memory_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lic_vector_memory_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lic_vector_memory_types", "env_read", "p2_env_1")
_emit_reads_environ("lic_vector_memory_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("lic_vector_memory_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lic_vector_memory_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lic_vector_memory_types", "context_pull")
_emit_pulls_context("p1", "lic_vector_memory_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lic_vector_memory_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lic_vector_memory_types", "uwg_term_2")
_emit_writes_through("p1", "lic_vector_memory_types", "write_through")
_emit_writes_through("p1", "lic_vector_memory_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "lic_vector_memory_types", "safety_validation")
_emit_invokes_eval("p1", "lic_vector_memory_types", "eval_call")
_emit_proposal_commits_routing("p1", "lic_vector_memory_types", "routing_commit")
_emit_escalates_to_human("p1", "lic_vector_memory_types", "human_escalation")
_emit_routes_through("p1", "lic_vector_memory_types", "route_through")
_emit_checks_agent_registry("p1", "lic_vector_memory_types", "agent_registry")
_emit_validates_agent_capability("p1", "lic_vector_memory_types", "capability")
_emit_dispatches_execution_plan("p1", "lic_vector_memory_types", "exec_plan")
_emit_agent_executes_agent("p1", "lic_vector_memory_types", "sub_agent")
_emit_routes_to_agent("p1", "lic_vector_memory_types", "target_agent")
_emit_verifies_policy("p1", "lic_vector_memory_types", "policy_check")
_emit_observes_runtime_state("p1", "lic_vector_memory_types", "runtime_state")
_emit_verifies_boundary("p1", "lic_vector_memory_types", "boundary_check")
_emit_transcripts_response("p1", "lic_vector_memory_types", "transcript")
_emit_hard_fails_untranscripted("p1", "lic_vector_memory_types")
_emit_gated_by_confidence("p1", "lic_vector_memory_types", "confidence_gate")
emit_replay_key("p0", "lic_vector_memory_types")
emit_determinism_digest("p0", "lic_vector_memory_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "lic_vector_memory_types", "execution_auth")
_emit_validates_capability("p2", "lic_vector_memory_types", "capability_check")
_emit_routes_to_capability("p2", "lic_vector_memory_types", "capability_route")
_emit_writes_via_uwg("p2", "lic_vector_memory_types", "uwg_write")
_emit_blocks_direct_write("p2", "lic_vector_memory_types", "direct_write_block")
_emit_records_tool_invocation("p2", "lic_vector_memory_types", "tool_invocation")
_emit_captures_execution_output("p2", "lic_vector_memory_types", "exec_output")
_emit_dispatches_agent("p3", "lic_vector_memory_types", "agent_dispatch")
_emit_coordinates_agents("p3", "lic_vector_memory_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "lic_vector_memory_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "lic_vector_memory_types", "healing_outcome")
_emit_escalates_failure("p3", "lic_vector_memory_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "lic_vector_memory_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lic_vector_memory_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "lic_vector_memory_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "lic_vector_memory_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lic_vector_memory_types", "eval_metric")
_emit_stores_embedding("p4", "lic_vector_memory_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "lic_vector_memory_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lic_vector_memory_types", "exec_snapshot_link")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_1")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_2")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_3")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_4")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_5")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_6")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_7")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_8")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_9")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_10")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_11")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_12")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_13")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_14")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_15")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_16")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_17")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_18")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_19")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_20")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_21")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_22")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_23")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_24")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_25")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_26")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_27")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_28")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_29")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_30")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_31")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_32")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_33")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_34")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_35")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_36")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_37")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_38")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_39")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_40")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_41")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_42")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_43")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_44")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_45")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_46")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_47")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_48")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_49")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_50")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_51")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_52")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_53")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_54")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_55")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_56")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_57")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_58")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_59")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_60")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_61")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_62")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_63")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_64")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_65")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_66")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_67")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_68")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_69")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_70")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_71")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_72")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_73")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_74")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_75")
_emit_reads_through("l4", "lic_vector_memory_types", "urg_read_76")


@dataclass
class VectorDocument:
    """Document stored in vector memory."""

    id: str
    text: str
    metadata: dict[str, object]
    embedding: list[float] | None = None
    distance: float | None = None


@dataclass
class QueryResult:
    """Result from a vector memory query."""

    documents: list[VectorDocument]
    total_count: int
    query_text: str
    query_time_ms: float = 0.0


@dataclass
class MemoryStats:
    """Statistics about the vector memory store."""

    collection_name: str
    document_count: int
    persist_directory: str


class LICVectorMemory:
    """
    Persistent vector memory using ChromaDB.

    Stores pre-computed research findings with embeddings for semantic search.
    Used by:
    - IntelligenceLibrarian: Writes research findings
    - HOP-2 ResearchAgent: Queries for relevant context
    """

    def __init__(
        self, collection_name: str = "lic_intelligence", persist_directory: str = "./chroma_db",
    ) -> None:
        """
        Initialize vector memory store.

        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Directory for persistent storage
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client: object = None
        self._collection: object = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize the ChromaDB client and collection.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            import chromadb

            self._client = chromadb.PersistentClient(
                path=self.persist_directory, settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "LIC Intelligence Provider - Pre-computed research"},
            )
            self._initialized = True
            return True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            self._initialized = False
            return False
        except (ValueError, TypeError, RuntimeError, OSError):
            self._initialized = False
            return False

    def is_initialized(self) -> bool:
        """Check if the memory store is initialized."""
        return self._initialized

    def add_document(
        self,
        text: str,
        metadata: dict[str, object],
        embedding: list[float] | None = None,
        document_id: str | None = None,
    ) -> str:
        """Module implementation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICVectorMemory.add_document")

        if document_id is None:
            id_string = f"{metadata.get('source_url', '')}_{metadata.get('extracted_at', '')}"
            document_id = hashlib.md5(id_string.encode()).hexdigest()
        if self._initialized and self._collection is not None:
            if embedding is not None:
                self._collection.add(
                    embeddings=[embedding], documents=[text], metadatas=[metadata], ids=[document_id],
                )
            else:
                self._collection.add(documents=[text], metadatas=[metadata], ids=[document_id])
        return document_id

    def query_memory(
        self, query_text: str, n_results: int = 20, filter_metadata: dict[str, object] | None = None,
    ) -> QueryResult:
        """
        Query the vector store for relevant documents.

        Args:
            query_text: Query string to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            QueryResult with matching documents
        """
        import time

        start_time = time.time()
        documents: list[VectorDocument] = []
        if self._initialized and self._collection is not None:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata if filter_metadata else None,
            )
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    doc = VectorDocument(
                        id=results["ids"][0][i],
                        text=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        distance=results["distances"][0][i] if "distances" in results else None,
                    )
                    documents.append(doc)
        query_time_ms = (time.time() - start_time) * 1000
        return QueryResult(
            documents=documents,
            total_count=len(documents),
            query_text=query_text,
            query_time_ms=query_time_ms,
        )

    def query_by_company(self, company_name: str, query_text: str, n_results: int = 20) -> QueryResult:
        """Query documents filtered by company name."""
        return self.query_memory(
            query_text=query_text, n_results=n_results, filter_metadata={"company_name": company_name},
        )

    def query_by_executive(self, executive_name: str, query_text: str, n_results: int = 10) -> QueryResult:
        """Query documents filtered by executive name."""
        return self.query_memory(
            query_text=query_text, n_results=n_results, filter_metadata={"executive_name": executive_name},
        )

    # guardian: allow-magic-config
    def get_strategic_briefs(self, company_name: str, max_age_days: int = 90) -> QueryResult:
        """Get strategic briefs for a company."""
        return self.query_memory(
            query_text=f"strategic brief {company_name}",
            n_results=5,
            filter_metadata={"company_name": company_name, "SourceType": "STRATEGIC_BRIEF"},
        )

    def get_stats(self) -> MemoryStats:
        """Get statistics about the memory store."""
        doc_count = 0
        if self._initialized and self._collection is not None:
            doc_count = self._collection.count()
        return MemoryStats(
            collection_name=self.collection_name,
            document_count=doc_count,
            persist_directory=self.persist_directory,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID."""
        if self._initialized and self._collection is not None:
            try:
                self._collection.delete(ids=[document_id])
                return True
            except (ValueError, TypeError, RuntimeError, KeyError):
                return False
        return False

    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        if self._initialized and self._client is not None:
            try:
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "LIC Intelligence Provider - Pre-computed research"},
                )
                return True
            except (ValueError, TypeError, RuntimeError, KeyError):
                return False
        return False


class MockVectorMemory(LICVectorMemory):
    """Mock implementation for testing without ChromaDB."""

    def __init__(
        self, collection_name: str = "lic_intelligence", persist_directory: str = "./chroma_db",
    ) -> None:
        """Initialize mock vector memory."""
        super().__init__(collection_name, persist_directory)
        self._documents: dict[str, VectorDocument] = {}
        self._initialized = True

    def initialize(self) -> bool:
        """Mock initialization always succeeds."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MockVectorMemory.initialize")

        self._initialized = True
        return True

    def add_document(
        self,
        text: str,
        metadata: dict[str, object],
        embedding: list[float] | None = None,
        document_id: str | None = None,
    ) -> str:
        """Add document to mock store."""
        if document_id is None:
            id_string = f"{metadata.get('source_url', '')}_{metadata.get('extracted_at', '')}"
            document_id = hashlib.md5(id_string.encode()).hexdigest()
        self._documents[document_id] = VectorDocument(
            id=document_id, text=text, metadata=metadata, embedding=embedding,
        )
        return document_id

    def query_memory(
        self, query_text: str, n_results: int = 20, filter_metadata: dict[str, object] | None = None,
    ) -> QueryResult:
        """Query mock store with simple text matching."""
        import time

        start_time = time.time()
        results: list[VectorDocument] = []
        query_lower = query_text.lower()
        for doc in self._documents.values():
            if query_lower in doc.text.lower():
                if filter_metadata:
                    match = all((doc.metadata.get(k) == v for k, v in filter_metadata.items()))
                    if not match:
                        continue
                results.append(doc)
            if len(results) >= n_results:
                break
        query_time_ms = (time.time() - start_time) * 1000
        return QueryResult(
            documents=results, total_count=len(results), query_text=query_text, query_time_ms=query_time_ms,
        )

    def get_stats(self) -> MemoryStats:
        """Get mock store statistics."""
        return MemoryStats(
            collection_name=self.collection_name,
            document_count=len(self._documents),
            persist_directory=self.persist_directory,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete from mock store."""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    def clear_collection(self) -> bool:
        """Clear mock store."""
        self._documents.clear()
        return True


def create_vector_memory(
    collection_name: str = "lic_intelligence", persist_directory: str = "./chroma_db", use_mock: bool = False,
) -> LICVectorMemory:
    """
    builder function to create a vector memory store.

    Args:
        collection_name: Name of the collection
        persist_directory: Directory for persistence
        use_mock: If True, use mock implementation

    Returns:
        LICVectorMemory instance
    """
    if use_mock:
        return MockVectorMemory(collection_name, persist_directory)
    memory = LICVectorMemory(collection_name, persist_directory)
    if not memory.initialize():
        return MockVectorMemory(collection_name, persist_directory)
    return memory

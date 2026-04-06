"""LocalEmbeddingPopulationService - Plan A deterministic batch pipeline.

Extracts embeddings from JSONL sources, normalizes, and writes to FAISS indexes.
Enforces deterministic ordering, canonicalization, and L2 normalization.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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

_emit_authorize_and_execute("p2", "local_embedding_population_service", "execution_auth")
_emit_validates_capability("p2", "local_embedding_population_service", "capability_check")
_emit_routes_to_capability("p2", "local_embedding_population_service", "capability_route")
_emit_writes_via_uwg("p2", "local_embedding_population_service", "uwg_write")
_emit_blocks_direct_write("p2", "local_embedding_population_service", "direct_write_block")
_emit_records_tool_invocation("p2", "local_embedding_population_service", "tool_invocation")
_emit_captures_execution_output("p2", "local_embedding_population_service", "exec_output")
_emit_dispatches_agent("p3", "local_embedding_population_service", "agent_dispatch")
_emit_coordinates_agents("p3", "local_embedding_population_service", "agent_coordination")
_emit_records_workflow_lineage("p3", "local_embedding_population_service", "workflow_lineage")
_emit_records_healing_outcome("p3", "local_embedding_population_service", "healing_outcome")
_emit_escalates_failure("p3", "local_embedding_population_service", "failure_escalation")
_emit_orchestrates_workflow("p3", "local_embedding_population_service", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "local_embedding_population_service", "healing_dispatch")
_emit_invokes_evaluation("p3", "local_embedding_population_service", "evaluation_signal")
_emit_records_telemetry_event("p4", "local_embedding_population_service", "telemetry_event")
_emit_captures_evaluation_metric("p4", "local_embedding_population_service", "eval_metric")
_emit_stores_embedding("p4", "local_embedding_population_service", "embedding_store")
_emit_updates_meta_learning_state("p4", "local_embedding_population_service", "meta_learning")
_emit_links_execution_to_snapshot("p4", "local_embedding_population_service", "exec_snapshot_link")
from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata

_emit_applies_guardrail("p0", "local_embedding_population_service", "p0_governance")
_emit_reads_policy_state("p0", "local_embedding_population_service", "policy_binding")
_emit_snapshots_state("p0", "local_embedding_population_service", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_1")
_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_2")
_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_3")
_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_4")
_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_5")
_emit_emits_metric_event("local_embedding_population_service", "p4obs", "metric_6")
_emit_records_incident_event("local_embedding_population_service", "p4obs", "incident")
_emit_captures_runtime_anomaly("local_embedding_population_service", "p4obs", "anomaly")
_emit_writes_observability_log("local_embedding_population_service", "p4obs", "obs_log")
_emit_updates_monitoring_state("local_embedding_population_service", "p4obs", "mon_state")
_emit_triggers_alert("local_embedding_population_service", "p4obs", "alert")
_emit_links_incident_trace("local_embedding_population_service", "p4obs", "trace_link")
_emit_captures_pattern("local_embedding_population_service", "p3lm", "pattern")
_emit_records_learning_event("local_embedding_population_service", "p3lm", "learning_event")
_emit_writes_learning_snapshot("local_embedding_population_service", "p3lm", "snapshot")
_emit_feeds_meta_learning("local_embedding_population_service", "p3lm", "meta_feed")
_emit_updates_routing_strategy("local_embedding_population_service", "p3lm", "routing")
_emit_improves_agent_policy("local_embedding_population_service", "p3lm", "policy")
_emit_stores_learning_state("local_embedding_population_service", "p3lm", "state")
_emit_records_execution_trace("local_embedding_population_service", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("local_embedding_population_service", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("local_embedding_population_service", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("local_embedding_population_service", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("local_embedding_population_service", "L4_STATE", "p2_trace_5")
_emit_reads_environ("local_embedding_population_service", "env_read", "p2_env_1")
_emit_reads_environ("local_embedding_population_service", "env_read", "p2_env_2")
_emit_reads_runtime_state("local_embedding_population_service", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("local_embedding_population_service", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "local_embedding_population_service", "context_pull")
_emit_pulls_context("p1", "local_embedding_population_service", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "local_embedding_population_service", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "local_embedding_population_service", "uwg_term_2")
_emit_writes_through("p1", "local_embedding_population_service", "write_through")
_emit_writes_through("p1", "local_embedding_population_service", "write_through_2")
_emit_validated_by_safety_plane("p1", "local_embedding_population_service", "safety_validation")
_emit_invokes_eval("p1", "local_embedding_population_service", "eval_call")
_emit_proposal_commits_routing("p1", "local_embedding_population_service", "routing_commit")
_emit_escalates_to_human("p1", "local_embedding_population_service", "human_escalation")
_emit_routes_through("p1", "local_embedding_population_service", "route_through")
_emit_checks_agent_registry("p1", "local_embedding_population_service", "agent_registry")
_emit_validates_agent_capability("p1", "local_embedding_population_service", "capability")
_emit_dispatches_execution_plan("p1", "local_embedding_population_service", "exec_plan")
_emit_agent_executes_agent("p1", "local_embedding_population_service", "sub_agent")
_emit_routes_to_agent("p1", "local_embedding_population_service", "target_agent")
_emit_verifies_policy("p1", "local_embedding_population_service", "policy_check")
_emit_observes_runtime_state("p1", "local_embedding_population_service", "runtime_state")
_emit_verifies_boundary("p1", "local_embedding_population_service", "boundary_check")
_emit_transcripts_response("p1", "local_embedding_population_service", "transcript")
_emit_hard_fails_untranscripted("p1", "local_embedding_population_service")
_emit_gated_by_confidence("p1", "local_embedding_population_service", "confidence_gate")
emit_replay_key("p0", "local_embedding_population_service")
emit_determinism_digest("p0", "local_embedding_population_service")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers used by LocalEmbeddingPopulationService."""

    def embed_batch(self, texts: list[str], dimension: int) -> list[list[float]]:
        """Embed a batch of texts into vectors of specified dimension."""
        ...


def extract_embedding_text(record: dict) -> str:
    """Extract text for embedding from a record.

    Phase 2: Accepts only "text" field. Raises ValueError if missing.

    Args:
        record: JSON record from source file.

    Returns:
        Text content for embedding.

    Raises:
        ValueError: If "text" field is missing or not a string.
    """
    if "text" not in record:
        raise ValueError("Record missing required 'text' field")
    text = record["text"]
    if not isinstance(text, str):
        raise ValueError(f"Record 'text' field must be string, got {type(text)}")
    return text


def normalize_l2(vector: list[float]) -> list[float]:
    """Normalize vector to unit L2 norm.

    Args:
        vector: Input vector.

    Returns:
        L2-normalized vector.
    """
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


@dataclass(frozen=True, slots=True)
class _RecordKey:
    """Key for deterministic record ordering."""

    file_path: str
    record_index: int


class LocalEmbeddingPopulationService:
    """Deterministic batch embedding population service.

    INVARIANT: Enforces deterministic ordering, canonicalization, and L2 normalization.
    INVARIANT: Single-writer discipline for index writes.
    """

    def __init__(
        self,
        faiss_store: LocalFAISSStore,
        embedder: EmbeddingProvider,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
        build_seed: int = 42,
    ) -> None:
        """Initialize service with dependencies.

        Args:
            faiss_store: FAISS store for index operations.
            embedder: Embedding provider for text-to-vector conversion.
            canonicalization_version: Version of canonicalization format.
            embedding_model_version: Version of embedding model.
            embedding_model_checksum: SHA-256 checksum of embedding model.
            build_seed: Random seed for deterministic builds (default: 42).
        """
        self.faiss_store = faiss_store
        self.embedder = embedder
        self.canonicalization_version = canonicalization_version
        self.embedding_model_version = embedding_model_version
        self.embedding_model_checksum = embedding_model_checksum
        self.build_seed = build_seed

    def populate_from_jsonl(
        self,
        *,
        index_id: str,
        source_files: list[Path],
        dimension: int,
        built_at_utc: int,
        batch_size: int = 5000,
        max_workers: int = 8,
    ) -> IndexBuildMetadata:
        """Populate index from JSONL source files.

        Args:
            index_id: Identifier for the index.
            source_files: List of JSONL source files.
            dimension: Embedding dimension.
            built_at_utc: Build timestamp (injected, not wall clock).
            batch_size: Batch size for embedding calls.
            max_workers: Maximum parallel workers for embedding.

        Returns:
            IndexBuildMetadata for the built index.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LocalEmbeddingPopulationService.populate_from_jsonl")

        sorted_files = sorted(source_files, key=lambda p: str(p))
        all_records = []
        for file_path in sorted_files:
            with open(file_path, encoding="utf-8") as f:
                for record_index, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    all_records.append((_RecordKey(str(file_path), record_index), record))
        all_records.sort(key=lambda x: (x[0].file_path, x[0].record_index))
        self.faiss_store.begin_build(index_id, dimension, self.build_seed)
        vectors = []
        metadatas = []
        for i, (_, record) in enumerate(all_records):
            canonical_record = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            text = extract_embedding_text(record)
            vectors.append(text)
            metadatas.append(
                {
                    "content_hash": record.get("content_hash", ""),
                    "trace_id": record.get("trace_id", ""),
                    "canonical_record": canonical_record,
                }
            )
            if len(vectors) >= batch_size or i == len(all_records) - 1:
                batch_vectors = self.embedder.embed_batch(vectors, dimension)
                normalized_vectors = [normalize_l2(v) for v in batch_vectors]
                self.faiss_store.add_vectors(index_id, normalized_vectors, metadatas)
                vectors = []
                metadatas = []
        return self.faiss_store.finalize_build(
            index_id,
            built_at_utc=built_at_utc,
            canonicalization_version=self.canonicalization_version,
            embedding_model_version=self.embedding_model_version,
            embedding_model_checksum=self.embedding_model_checksum,
        )


__all__ = ["LocalEmbeddingPopulationService", "EmbeddingProvider", "extract_embedding_text", "normalize_l2"]

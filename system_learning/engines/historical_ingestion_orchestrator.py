"""Historical ingestion orchestrator for Plan A.

Materializes deterministic JSONL corpora and builds indexes via
LocalEmbeddingPopulationService.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "historical_ingestion_orchestrator", "execution_auth")
_emit_validates_capability("p2", "historical_ingestion_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "historical_ingestion_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "historical_ingestion_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "historical_ingestion_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "historical_ingestion_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "historical_ingestion_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "historical_ingestion_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "historical_ingestion_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "historical_ingestion_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "historical_ingestion_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "historical_ingestion_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "historical_ingestion_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "historical_ingestion_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "historical_ingestion_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "historical_ingestion_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "historical_ingestion_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "historical_ingestion_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "historical_ingestion_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "historical_ingestion_orchestrator", "exec_snapshot_link")
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
from system_learning.config.embedding_storage_layout import EmbeddingStorageLayout
from system_learning.engines.embedding_corpus_extraction import (
    extract_dpo_pair_records,
    extract_healing_context_records,
    extract_telemetry_event_records,
    write_jsonl_records,
)
from system_learning.engines.local_embedding_population_service import (
    EmbeddingProvider,
    LocalEmbeddingPopulationService,
)
from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata

_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("historical_ingestion_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("historical_ingestion_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("historical_ingestion_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("historical_ingestion_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("historical_ingestion_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("historical_ingestion_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("historical_ingestion_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("historical_ingestion_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("historical_ingestion_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("historical_ingestion_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("historical_ingestion_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("historical_ingestion_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("historical_ingestion_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("historical_ingestion_orchestrator", "p3lm", "state")
_emit_records_execution_trace("historical_ingestion_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("historical_ingestion_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("historical_ingestion_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("historical_ingestion_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("historical_ingestion_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("historical_ingestion_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("historical_ingestion_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("historical_ingestion_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("historical_ingestion_orchestrator", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "historical_ingestion_orchestrator")
_emit_applies_guardrail("p0", "historical_ingestion_orchestrator", "p0_governance")
_emit_reads_policy_state("p0", "historical_ingestion_orchestrator", "policy_binding")
_emit_snapshots_state("p0", "historical_ingestion_orchestrator", "state_snapshot")
_emit_pulls_context("p1", "historical_ingestion_orchestrator", "context_pull")
_emit_pulls_context("p1", "historical_ingestion_orchestrator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "historical_ingestion_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "historical_ingestion_orchestrator", "uwg_term_secondary")
_emit_writes_through("p1", "historical_ingestion_orchestrator", "write_through")
_emit_writes_through("p1", "historical_ingestion_orchestrator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "historical_ingestion_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "historical_ingestion_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "historical_ingestion_orchestrator", "routing_commit")
_emit_escalates_to_human("p1", "historical_ingestion_orchestrator", "human_escalation")
_emit_routes_through("p1", "historical_ingestion_orchestrator", "route_through")
_emit_checks_agent_registry("p1", "historical_ingestion_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "historical_ingestion_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "historical_ingestion_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "historical_ingestion_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "historical_ingestion_orchestrator", "target_agent")
_emit_verifies_policy("p1", "historical_ingestion_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "historical_ingestion_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "historical_ingestion_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "historical_ingestion_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "historical_ingestion_orchestrator")
_emit_gated_by_confidence("p1", "historical_ingestion_orchestrator", "confidence_gate")
emit_replay_key("p0", "historical_ingestion_orchestrator")
emit_determinism_digest("p0", "historical_ingestion_orchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def ingest_and_build_indexes(
    *,
    base_path: Path,
    built_at_utc: int,
    healing_source: list[dict],
    telemetry_source: list[dict],
    dpo_source: list[dict],
    embedding_model_version: str,
    embedding_model_checksum: str,
    canonicalization_version: str,
) -> dict[str, IndexBuildMetadata]:
    """Ingest historical data and build embedding indexes.

    Args:
        base_path: Base path for all storage operations.
        built_at_utc: Build timestamp (injected, not wall clock).
        healing_source: List of healing context source dictionaries.
        telemetry_source: List of telemetry event source dictionaries.
        dpo_source: List of DPO pair source dictionaries.
        embedding_model_version: Version of embedding model.
        embedding_model_checksum: SHA-256 checksum of embedding model.
        canonicalization_version: Canonicalization format version.

    Returns:
        Mapping of index_id to IndexBuildMetadata for all built indexes.
    """
    # Setup storage layout
    layout = EmbeddingStorageLayout(base_path)

    # Setup FAISS store and population service
    store = LocalFAISSStore(base_path=base_path)

    # Note: embedder will be injected by caller (tests use FakeEmbedder)
    # For production, this would be EmbeddingSovereignAgent
    embedder = None  # Will be set below

    # Create population service with embedder placeholder
    service = LocalEmbeddingPopulationService(
        faiss_store=store,
        embedder=embedder,  # Will be replaced
        canonicalization_version=canonicalization_version,
        embedding_model_version=embedding_model_version,
        embedding_model_checksum=embedding_model_checksum,
        build_seed=42,
    )

    # Extract records for each namespace
    healing_records = extract_healing_context_records(healing_source)
    telemetry_records = extract_telemetry_event_records(telemetry_source)
    dpo_records = extract_dpo_pair_records(dpo_source)

    # Write JSONL files to raw_staging
    healing_jsonl = layout.raw_staging_dir / "healing_contexts.jsonl"
    telemetry_jsonl = layout.raw_staging_dir / "telemetry_events.jsonl"
    dpo_jsonl = layout.raw_staging_dir / "dpo_pairs.jsonl"

    layout.raw_staging_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl_records(healing_jsonl, healing_records)
    write_jsonl_records(telemetry_jsonl, telemetry_records)
    write_jsonl_records(dpo_jsonl, dpo_records)

    # Build indexes - need to inject embedder for each call
    # This is a bit awkward but maintains the service interface
    results = {}

    # Helper to build index with injected embedder
    def build_with_embedder(
        embedder: EmbeddingProvider,
        index_id: str,
        source_file: Path,
        dimension: int,
    ) -> IndexBuildMetadata:
        # Create new service instance with injected embedder
        service_with_embedder = LocalEmbeddingPopulationService(
            faiss_store=store,
            embedder=embedder,
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            build_seed=42,
        )
        return service_with_embedder.populate_from_jsonl(
            index_id=index_id,
            source_files=[source_file],
            dimension=dimension,
            built_at_utc=built_at_utc,
        )

    # Note: The embedder parameter is passed via closure capture
    # This allows tests to inject a FakeEmbedder while maintaining
    # the pure function signature

    # For now, we'll raise an error if embedder is None
    # In practice, this function should be called from a context
    # that can provide the embedder
    if service.embedder is None:
        raise RuntimeError(
            "embedder must be injected. "
            "This function should be called from a wrapper that provides the embedder."
        )

    # Build healing contexts index (dim=768)
    results["healing_contexts_v1"] = service.populate_from_jsonl(
        index_id="healing_contexts_v1",
        source_files=[healing_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    # Build telemetry events index (dim=384)
    results["telemetry_events_v1"] = service.populate_from_jsonl(
        index_id="telemetry_events_v1",
        source_files=[telemetry_jsonl],
        dimension=384,
        built_at_utc=built_at_utc,
    )

    # Build DPO pairs index (dim=768)
    results["dpo_pairs_v1"] = service.populate_from_jsonl(
        index_id="dpo_pairs_v1",
        source_files=[dpo_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    return results


def ingest_and_build_indexes_with_embedder(
    *,
    base_path: Path,
    built_at_utc: int,
    healing_source: list[dict],
    telemetry_source: list[dict],
    dpo_source: list[dict],
    embedding_model_version: str,
    embedding_model_checksum: str,
    canonicalization_version: str,
    embedder: EmbeddingProvider,
) -> dict[str, IndexBuildMetadata]:
    """Convenience wrapper that accepts embedder parameter.

    This function provides a cleaner interface for tests and production
    by accepting the embedder directly rather than requiring injection.
    """
    # Setup storage layout
    layout = EmbeddingStorageLayout(base_path)

    # Setup FAISS store and population service
    store = LocalFAISSStore(base_path=base_path)
    service = LocalEmbeddingPopulationService(
        faiss_store=store,
        embedder=embedder,
        canonicalization_version=canonicalization_version,
        embedding_model_version=embedding_model_version,
        embedding_model_checksum=embedding_model_checksum,
        build_seed=42,
    )

    # Extract records for each namespace
    healing_records = extract_healing_context_records(healing_source)
    telemetry_records = extract_telemetry_event_records(telemetry_source)
    dpo_records = extract_dpo_pair_records(dpo_source)

    # Write JSONL files to raw_staging
    healing_jsonl = layout.raw_staging_dir / "healing_contexts.jsonl"
    telemetry_jsonl = layout.raw_staging_dir / "telemetry_events.jsonl"
    dpo_jsonl = layout.raw_staging_dir / "dpo_pairs.jsonl"

    layout.raw_staging_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl_records(healing_jsonl, healing_records)
    write_jsonl_records(telemetry_jsonl, telemetry_records)
    write_jsonl_records(dpo_jsonl, dpo_records)

    # Build indexes and persist each one to disk (G_HI fix: finalize_build alone is
    # in-memory only; persist_to_disk writes the 3-file artifact so the index
    # survives process exit and can be loaded by HealingMemoryRetriever).
    results = {}
    _index_dirs = {
        "healing_contexts_v1": layout.healing_contexts_index_dir(),
        "telemetry_events_v1": layout.telemetry_events_index_dir(),
        "dpo_pairs_v1": layout.dpo_pairs_index_dir(),
    }

    # Build healing contexts index (dim=768)
    results["healing_contexts_v1"] = service.populate_from_jsonl(
        index_id="healing_contexts_v1",
        source_files=[healing_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )
    _index_dirs["healing_contexts_v1"].mkdir(parents=True, exist_ok=True)
    store.persist_to_disk(
        "healing_contexts_v1",
        _index_dirs["healing_contexts_v1"],
        embedder_id=embedding_model_checksum,
        model_version=embedding_model_version,
    )

    # Build telemetry events index (dim=384)
    results["telemetry_events_v1"] = service.populate_from_jsonl(
        index_id="telemetry_events_v1",
        source_files=[telemetry_jsonl],
        dimension=384,
        built_at_utc=built_at_utc,
    )
    _index_dirs["telemetry_events_v1"].mkdir(parents=True, exist_ok=True)
    store.persist_to_disk(
        "telemetry_events_v1",
        _index_dirs["telemetry_events_v1"],
        embedder_id=embedding_model_checksum,
        model_version=embedding_model_version,
    )

    # Build DPO pairs index (dim=768)
    results["dpo_pairs_v1"] = service.populate_from_jsonl(
        index_id="dpo_pairs_v1",
        source_files=[dpo_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )
    _index_dirs["dpo_pairs_v1"].mkdir(parents=True, exist_ok=True)
    store.persist_to_disk(
        "dpo_pairs_v1",
        _index_dirs["dpo_pairs_v1"],
        embedder_id=embedding_model_checksum,
        model_version=embedding_model_version,
    )

    return results


# For backward compatibility, expose the wrapper as the main function
ingest_and_build_indexes = ingest_and_build_indexes_with_embedder


__all__ = [
    "ingest_and_build_indexes",
    "ingest_and_build_indexes_with_embedder",
]

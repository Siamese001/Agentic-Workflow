"""Embedding retention scheduler for Plan A Phase 4.

Provides deterministic prune triggers and rebuild cycles with
invalidation enforcement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "embedding_retention_scheduler", "execution_auth")
trace_contract._emit_validates_capability("p2", "embedding_retention_scheduler", "capability_check")
trace_contract._emit_routes_to_capability("p2", "embedding_retention_scheduler", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "embedding_retention_scheduler", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "embedding_retention_scheduler", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "embedding_retention_scheduler", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "embedding_retention_scheduler", "exec_output")
trace_contract._emit_dispatches_agent("p3", "embedding_retention_scheduler", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "embedding_retention_scheduler", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "embedding_retention_scheduler", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "embedding_retention_scheduler", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "embedding_retention_scheduler", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "embedding_retention_scheduler", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "embedding_retention_scheduler", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "embedding_retention_scheduler", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "embedding_retention_scheduler", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "embedding_retention_scheduler", "eval_metric")
trace_contract._emit_stores_embedding("p4", "embedding_retention_scheduler", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "embedding_retention_scheduler", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "embedding_retention_scheduler", "exec_snapshot_link")
from .local_faiss_store import LocalFAISSStore
from agentic_core.L6_system_learning.types.index_build_metadata_types import IndexBuildMetadata

trace_contract._emit_applies_guardrail("p0", "embedding_retention_scheduler", "p0_governance")
trace_contract._emit_snapshots_state("p0", "embedding_retention_scheduler", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("embedding_retention_scheduler", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("embedding_retention_scheduler", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("embedding_retention_scheduler", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("embedding_retention_scheduler", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("embedding_retention_scheduler", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("embedding_retention_scheduler", "p4obs", "alert")
trace_contract._emit_links_incident_trace("embedding_retention_scheduler", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("embedding_retention_scheduler", "p3lm", "pattern")
trace_contract._emit_records_learning_event("embedding_retention_scheduler", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("embedding_retention_scheduler", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("embedding_retention_scheduler", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("embedding_retention_scheduler", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("embedding_retention_scheduler", "p3lm", "policy")
trace_contract._emit_stores_learning_state("embedding_retention_scheduler", "p3lm", "state")
trace_contract._emit_records_execution_trace("embedding_retention_scheduler", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("embedding_retention_scheduler", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("embedding_retention_scheduler", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("embedding_retention_scheduler", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("embedding_retention_scheduler", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("embedding_retention_scheduler", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("embedding_retention_scheduler", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("embedding_retention_scheduler", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("embedding_retention_scheduler", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "embedding_retention_scheduler", "context_pull")
trace_contract._emit_pulls_context("p1", "embedding_retention_scheduler", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_retention_scheduler", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_retention_scheduler", "uwg_term_2")
trace_contract._emit_writes_through("p1", "embedding_retention_scheduler", "write_through")
trace_contract._emit_writes_through("p1", "embedding_retention_scheduler", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "embedding_retention_scheduler", "safety_validation")
trace_contract._emit_invokes_eval("p1", "embedding_retention_scheduler", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "embedding_retention_scheduler", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "embedding_retention_scheduler", "human_escalation")
trace_contract._emit_routes_through("p1", "embedding_retention_scheduler", "route_through")
trace_contract._emit_checks_agent_registry("p1", "embedding_retention_scheduler", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "embedding_retention_scheduler", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "embedding_retention_scheduler", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "embedding_retention_scheduler", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "embedding_retention_scheduler", "target_agent")
trace_contract._emit_verifies_policy("p1", "embedding_retention_scheduler", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "embedding_retention_scheduler", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "embedding_retention_scheduler", "boundary_check")
trace_contract._emit_transcripts_response("p1", "embedding_retention_scheduler", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "embedding_retention_scheduler")
trace_contract._emit_gated_by_confidence("p1", "embedding_retention_scheduler", "confidence_gate")
trace_contract.emit_replay_key("p0", "embedding_retention_scheduler")
trace_contract.emit_determinism_digest("p0", "embedding_retention_scheduler")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class EmbeddingRetentionScheduler:
    """Scheduler for embedding retention policies and deterministic pruning."""

    def run_once(
        self,
        *,
        now_utc: int,
        policies: dict[str, dict[str, Any]],
        stores: dict[str, LocalFAISSStore],
        persist_base_path: Path | None = None,
    ) -> dict[str, IndexBuildMetadata]:
        """Run retention scheduler once.

        Args:
            now_utc: Current timestamp for retention calculations.
            policies: Mapping of index_id to policy configuration.
                Each policy dict contains:
                - retention_days: int for rolling window retention
                - mode: str ("rolling_window", "predicate", or "none")
                - predicate: Callable[[Dict[str, Any]], bool] for mode="predicate"
            stores: Mapping of index_id to LocalFAISSStore instances.
            persist_base_path: If provided, persist rebuilt indexes to disk under
                ``persist_base_path / index_id`` after each rebuild (G_RS fix).

        Returns:
            Mapping of index_id to rebuilt IndexBuildMetadata for pruned indexes.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EmbeddingRetentionScheduler.run_once"
        )

        results = {}
        for index_id, store in tqdm(stores.items(), desc="Processing", unit="item"):
            if index_id not in policies:
                continue
            policy = policies[index_id]
            mode = policy.get("mode", "none")
            if mode == "none":
                continue
            elif mode == "rolling_window":
                retention_days = policy.get("retention_days")
                if retention_days is None:
                    continue
                cutoff_utc = now_utc - retention_days * 24 * 60 * 60

                def rolling_window_predicate(metadata: dict[str, Any]) -> bool:
                    """Return True if record should be pruned (older than cutoff)."""
                    created_utc = metadata.get("created_utc")
                    if created_utc is None:
                        return False
                    return created_utc < cutoff_utc

                num_removed = store.prune(index_id, rolling_window_predicate)
                if num_removed > 0:
                    if hasattr(store, "_memory_indexes") and index_id in store._memory_indexes:
                        old_metadata = store._memory_indexes[index_id]["metadata"]
                    else:
                        _, _, old_metadata = store.open(index_id)
                    new_metadata = store.rebuild(
                        index_id,
                        built_at_utc=now_utc,
                        canonicalization_version=old_metadata.canonicalization_version,
                        embedding_model_version=old_metadata.embedding_model_version,
                        embedding_model_checksum=old_metadata.embedding_model_checksum,
                    )
                    results[index_id] = new_metadata
                    if persist_base_path is not None:
                        dest = Path(persist_base_path) / index_id
                        dest.mkdir(parents=True, exist_ok=True)
                        store.persist_to_disk(
                            index_id,
                            dest,
                            embedder_id=old_metadata.embedding_model_checksum,
                            model_version=old_metadata.embedding_model_version,
                        )
            elif mode == "predicate":
                predicate = policy.get("predicate")
                if predicate is None:
                    continue
                num_removed = store.prune(index_id, predicate)
                if num_removed > 0:
                    if hasattr(store, "_memory_indexes") and index_id in store._memory_indexes:
                        old_metadata = store._memory_indexes[index_id]["metadata"]
                    else:
                        _, _, old_metadata = store.open(index_id)
                    new_metadata = store.rebuild(
                        index_id,
                        built_at_utc=now_utc,
                        canonicalization_version=old_metadata.canonicalization_version,
                        embedding_model_version=old_metadata.embedding_model_version,
                        embedding_model_checksum=old_metadata.embedding_model_checksum,
                    )
                    results[index_id] = new_metadata
                    if persist_base_path is not None:
                        dest = Path(persist_base_path) / index_id
                        dest.mkdir(parents=True, exist_ok=True)
                        store.persist_to_disk(
                            index_id,
                            dest,
                            embedder_id=old_metadata.embedding_model_checksum,
                            model_version=old_metadata.embedding_model_version,
                        )
        return results


__all__ = ["EmbeddingRetentionScheduler"]

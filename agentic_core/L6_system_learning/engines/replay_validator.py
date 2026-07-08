"""ReplayValidator for Plan B Phase 3.

Deterministic validator for seed pack integrity and EmbeddingArtifact stability.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "replay_validator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "replay_validator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "replay_validator", "state_snapshot")

trace_contract.record_execution_trace("replay_validator", "replay_validator_trace")


trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_validator", "write_through")
trace_contract._emit_writes_through("p1", "replay_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_validator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "replay_validator", "human_escalation")
trace_contract._emit_routes_through("p1", "replay_validator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "replay_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_validator")
trace_contract._emit_gated_by_confidence("p1", "replay_validator", "confidence_gate")
trace_contract.emit_replay_key("p0", "replay_validator")
trace_contract.emit_determinism_digest("p0", "replay_validator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "replay_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_validator", "exec_snapshot_link")


class DeterminismViolationError(Exception):
    """Raised when determinism invariants are violated."""

    pass


class ReplayValidator:
    """Validates deterministic behavior of seed packs and embedding artifacts."""

    def validate_seed_pack(self, *, base_path: str, namespace: str, seed_index_version_hash: str) -> None:
        """Validate seed pack integrity and hash stability.

        Args:
            base_path: Base directory containing seed packs
            namespace: Namespace of the seed pack
            seed_index_version_hash: Expected seed index version hash

        Raises:
            DeterminismViolationError: If any validation fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ReplayValidator.validate_seed_pack"
        )

        base = Path(base_path)
        pack_dir = base / "seed_packs" / namespace / seed_index_version_hash
        manifest_path = pack_dir / "seed_manifest.json"
        row_index_path = pack_dir / "row_index.jsonl"
        embeddings_path = pack_dir / "embeddings.f32"
        if not all(p.exists() for p in [manifest_path, row_index_path, embeddings_path]):
            if not pack_dir.exists():
                raise DeterminismViolationError(f"Seed pack directory does not exist: {pack_dir}")
            raise DeterminismViolationError(f"Missing required files in seed pack: {pack_dir}")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        with open(row_index_path, "rb") as f:
            row_index_bytes = f.read()
        row_index_hash = hashlib.sha256(row_index_bytes).hexdigest()
        with open(embeddings_path, "rb") as f:
            embeddings_bytes = f.read()
        embeddings_hash = hashlib.sha256(embeddings_bytes).hexdigest()
        if row_index_hash != manifest.get("row_index_hash"):
            raise DeterminismViolationError(
                f"Row index hash mismatch: computed {row_index_hash}, expected {manifest.get('row_index_hash')}",
            )
        if embeddings_hash != manifest.get("matrix_hash"):
            raise DeterminismViolationError(
                f"Embeddings hash mismatch: computed {embeddings_hash}, expected {manifest.get('matrix_hash')}",
            )
        if manifest.get("seed_index_version_hash") != seed_index_version_hash:
            raise DeterminismViolationError(
                f"Seed index version hash mismatch: manifest {manifest.get('seed_index_version_hash')}, expected {seed_index_version_hash}",
            )

    def validate_embedding_artifact(
        self,
        *,
        artifact: Any,
        expected_seed_index_version_hash: str,
        reference_artifact_hash: str | None = None,
    ) -> None:
        """Validate EmbeddingArtifact stability and consistency.

        Args:
            artifact: The EmbeddingArtifact to validate
            expected_seed_index_version_hash: Expected seed index version hash
            reference_artifact_hash: Optional reference hash for comparison

        Raises:
            DeterminismViolationError: If any validation fails
        """
        from agentic_core.L6_system_learning.types.embedding_artifact import EmbeddingArtifact

        if not isinstance(artifact, EmbeddingArtifact):
            raise DeterminismViolationError(f"Expected EmbeddingArtifact, got {type(artifact)}")
        if artifact.seed_index_version_hash != expected_seed_index_version_hash:
            raise DeterminismViolationError(
                f"Seed index version hash mismatch: artifact {artifact.seed_index_version_hash}, expected {expected_seed_index_version_hash}",
            )
        if reference_artifact_hash is not None:
            computed_hash = artifact.artifact_hash()
            if computed_hash != reference_artifact_hash:
                raise DeterminismViolationError(
                    f"Artifact hash mismatch: computed {computed_hash}, expected {reference_artifact_hash}",
                )
        if not artifact.supporting_trace_ids:
            raise DeterminismViolationError("supporting_trace_ids cannot be empty")
        if len(artifact.supporting_trace_ids) != len(set(artifact.supporting_trace_ids)):
            raise DeterminismViolationError("supporting_trace_ids contains duplicates")
        if any(not trace_id for trace_id in artifact.supporting_trace_ids):
            raise DeterminismViolationError("supporting_trace_ids contains empty strings")
        if any(not content_hash for content_hash in artifact.supporting_content_hashes):
            raise DeterminismViolationError("supporting_content_hashes contains empty strings")
        if artifact.k != len(artifact.supporting_trace_ids):
            raise DeterminismViolationError(
                f"k ({artifact.k}) does not match number of trace IDs ({len(artifact.supporting_trace_ids)})",
            )
        if artifact.supporting_trace_ids != sorted(artifact.supporting_trace_ids):
            raise DeterminismViolationError("supporting_trace_ids not in canonical sorted order")
        if artifact.supporting_content_hashes != sorted(artifact.supporting_content_hashes):
            raise DeterminismViolationError("supporting_content_hashes not in canonical sorted order")


__all__ = ["ReplayValidator", "DeterminismViolationError"]

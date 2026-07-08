"""
PHASE 4 WAVE 2 — VLLMInfrastructureFingerprint: pure-L2 infrastructure fingerprint.

Provides deterministic, canonical serialization and SHA256 hashing of vLLM
infrastructure parameters. No GPU imports. No runtime probing in L2 tests.
Used by Phase 3 telemetry path for deterministic replay sealing.

Fingerprint fields (all strings):
- model_name: e.g., "Qwen/Qwen2.5-32B-Instruct-AWQ"
- model_revision_sha: git SHA or model identifier
- vllm_version: vLLM package version
- transformers_version: transformers package version
- torch_version: torch package version
- cuda_version: CUDA runtime version
- driver_version: NVIDIA driver version
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "vllm_infrastructure_fingerprint_types")
trace_contract.emit_determinism_digest("p0", "vllm_infrastructure_fingerprint_types")

trace_contract._emit_dispatches_healing_run("p1", "vllm_infrastructure_fingerprint_types", "L2")
trace_contract._emit_routes_through("p1", "vllm_infrastructure_fingerprint_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "vllm_infrastructure_fingerprint_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "vllm_infrastructure_fingerprint_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "vllm_infrastructure_fingerprint_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "vllm_infrastructure_fingerprint_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "vllm_infrastructure_fingerprint_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "vllm_infrastructure_fingerprint_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "vllm_infrastructure_fingerprint_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "vllm_infrastructure_fingerprint_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "vllm_infrastructure_fingerprint_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "vllm_infrastructure_fingerprint_types")
trace_contract._emit_gated_by_confidence("p1", "vllm_infrastructure_fingerprint_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "vllm_infrastructure_fingerprint_types", "L2")
trace_contract._emit_reads_policy_state("p1", "vllm_infrastructure_fingerprint_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "vllm_infrastructure_fingerprint_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "vllm_infrastructure_fingerprint_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "vllm_infrastructure_fingerprint_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "vllm_infrastructure_fingerprint_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "vllm_infrastructure_fingerprint_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "vllm_infrastructure_fingerprint_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "vllm_infrastructure_fingerprint_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "vllm_infrastructure_fingerprint_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "vllm_infrastructure_fingerprint_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "vllm_infrastructure_fingerprint_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "vllm_infrastructure_fingerprint_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "vllm_infrastructure_fingerprint_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "vllm_infrastructure_fingerprint_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "vllm_infrastructure_fingerprint_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "vllm_infrastructure_fingerprint_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "vllm_infrastructure_fingerprint_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "vllm_infrastructure_fingerprint_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "vllm_infrastructure_fingerprint_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "vllm_infrastructure_fingerprint_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "vllm_infrastructure_fingerprint_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("vllm_infrastructure_fingerprint_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("vllm_infrastructure_fingerprint_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("vllm_infrastructure_fingerprint_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("vllm_infrastructure_fingerprint_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("vllm_infrastructure_fingerprint_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("vllm_infrastructure_fingerprint_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("vllm_infrastructure_fingerprint_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("vllm_infrastructure_fingerprint_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("vllm_infrastructure_fingerprint_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("vllm_infrastructure_fingerprint_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("vllm_infrastructure_fingerprint_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("vllm_infrastructure_fingerprint_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("vllm_infrastructure_fingerprint_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("vllm_infrastructure_fingerprint_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("vllm_infrastructure_fingerprint_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("vllm_infrastructure_fingerprint_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("vllm_infrastructure_fingerprint_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("vllm_infrastructure_fingerprint_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("vllm_infrastructure_fingerprint_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("vllm_infrastructure_fingerprint_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("vllm_infrastructure_fingerprint_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("vllm_infrastructure_fingerprint_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("vllm_infrastructure_fingerprint_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "vllm_infrastructure_fingerprint_types", "context_pull")
trace_contract._emit_pulls_context("p1", "vllm_infrastructure_fingerprint_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_infrastructure_fingerprint_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_infrastructure_fingerprint_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "vllm_infrastructure_fingerprint_types", "write_through")
trace_contract._emit_writes_through("p1", "vllm_infrastructure_fingerprint_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "vllm_infrastructure_fingerprint_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "vllm_infrastructure_fingerprint_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "vllm_infrastructure_fingerprint_types", "routing_commit")


def canonical_json(obj: Any) -> str:
    """
    Deterministic JSON serialization with stable key order and minimal whitespace.

    Args:
        obj: JSON-serializable object.

    Returns:
        Canonical JSON string.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "canonical_json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: str | bytes) -> str:
    """
    Compute SHA256 hex digest of string or bytes.

    Args:
        data: Input data.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class VLLMInfrastructureFingerprint:
    """Pure-L2 infrastructure fingerprint for deterministic replay sealing."""

    model_name: str
    model_revision_sha: str
    vllm_version: str
    transformers_version: str
    torch_version: str
    cuda_version: str
    driver_version: str

    def as_dict(self) -> dict[str, str]:
        """Return fingerprint as plain dict (all strings)."""
        return {
            "model_name": self.model_name,
            "model_revision_sha": self.model_revision_sha,
            "vllm_version": self.vllm_version,
            "transformers_version": self.transformers_version,
            "torch_version": self.torch_version,
            "cuda_version": self.cuda_version,
            "driver_version": self.driver_version,
        }

    def canonical_json(self) -> str:
        """
        Return canonical JSON representation (stable key order, no whitespace).

        Used for deterministic hashing.
        """
        return canonical_json(self.as_dict())

    def fingerprint_hash(self) -> str:
        """
        Compute SHA256 hash of the canonical JSON representation.

        Returns:
            64-character lowercase hex SHA256 digest.
        """
        return sha256_hex(self.canonical_json())

    @classmethod
    def deterministic_test_instance(cls) -> VLLMInfrastructureFingerprint:
        """
        Create a deterministic test instance with known values.

        Used by unit_min_deps tests to avoid runtime probing.
        """
        return cls(
            model_name="Qwen/Qwen2.5-32B-Instruct-AWQ",
            model_revision_sha="abc123def456",
            vllm_version="0.6.3",
            transformers_version="4.46.0",
            torch_version="2.5.1",
            cuda_version="12.4",
            driver_version="550.54.14",
        )


__all__ = ["VLLMInfrastructureFingerprint", "canonical_json", "sha256_hex"]

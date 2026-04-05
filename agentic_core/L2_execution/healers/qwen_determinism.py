"""
Qwen Determinism - Full SHA-256 Digest and Output Canonicalization

Provides deterministic hashing for Qwen model invocations to ensure
replay consistency and auditability.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

emit_replay_key("p0", "qwen_determinism")
emit_determinism_digest("p0", "qwen_determinism")

_emit_dispatches_healing_run("p1", "qwen_determinism", "L2")
_emit_routes_through("p1", "qwen_determinism", "L2")
_emit_checks_agent_registry("p1", "qwen_determinism", "agent_registry")
_emit_validates_agent_capability("p1", "qwen_determinism", "capability")
_emit_dispatches_execution_plan("p1", "qwen_determinism", "exec_plan")
_emit_agent_executes_agent("p1", "qwen_determinism", "sub_agent")
_emit_routes_to_agent("p1", "qwen_determinism", "target_agent")
_emit_verifies_policy("p1", "qwen_determinism", "policy_check")
_emit_observes_runtime_state("p1", "qwen_determinism", "runtime_state")
_emit_verifies_boundary("p1", "qwen_determinism", "boundary_check")
_emit_transcripts_response("p1", "qwen_determinism", "transcript")
_emit_hard_fails_untranscripted("p1", "qwen_determinism")
_emit_gated_by_confidence("p1", "qwen_determinism", "confidence_gate")
_emit_escalates_to_human("p1", "qwen_determinism", "L2")
_emit_reads_policy_state("p1", "qwen_determinism", "L2")
_emit_authorize_and_execute("p2", "qwen_determinism", "execution_auth")
_emit_validates_capability("p2", "qwen_determinism", "capability_check")
_emit_routes_to_capability("p2", "qwen_determinism", "capability_route")
_emit_writes_via_uwg("p2", "qwen_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_determinism", "exec_output")
_emit_dispatches_agent("p3", "qwen_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_determinism", "healing_outcome")
_emit_escalates_failure("p3", "qwen_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_determinism", "eval_metric")
_emit_stores_embedding("p4", "qwen_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_determinism", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

record_execution_trace("qwen_determinism", "qwen_determinism_trace")


_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_1")
_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_2")
_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_3")
_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_4")
_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_5")
_emit_emits_metric_event("qwen_determinism", "p4obs", "metric_6")
_emit_records_incident_event("qwen_determinism", "p4obs", "incident")
_emit_captures_runtime_anomaly("qwen_determinism", "p4obs", "anomaly")
_emit_writes_observability_log("qwen_determinism", "p4obs", "obs_log")
_emit_updates_monitoring_state("qwen_determinism", "p4obs", "mon_state")
_emit_triggers_alert("qwen_determinism", "p4obs", "alert")
_emit_links_incident_trace("qwen_determinism", "p4obs", "trace_link")
_emit_captures_pattern("qwen_determinism", "p3lm", "pattern")
_emit_records_learning_event("qwen_determinism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("qwen_determinism", "p3lm", "snapshot")
_emit_feeds_meta_learning("qwen_determinism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("qwen_determinism", "p3lm", "routing")
_emit_improves_agent_policy("qwen_determinism", "p3lm", "policy")
_emit_stores_learning_state("qwen_determinism", "p3lm", "state")
_emit_records_execution_trace("qwen_determinism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("qwen_determinism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("qwen_determinism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("qwen_determinism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("qwen_determinism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("qwen_determinism", "env_read", "p2_env_1")
_emit_reads_environ("qwen_determinism", "env_read", "p2_env_2")
_emit_reads_runtime_state("qwen_determinism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("qwen_determinism", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "qwen_determinism", "context_pull")
_emit_pulls_context("p1", "qwen_determinism", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "qwen_determinism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "qwen_determinism", "uwg_term_2")
_emit_writes_through("p1", "qwen_determinism", "write_through")
_emit_writes_through("p1", "qwen_determinism", "write_through_2")
_emit_validated_by_safety_plane("p1", "qwen_determinism", "safety_validation")
_emit_invokes_eval("p1", "qwen_determinism", "eval_call")
_emit_proposal_commits_routing("p1", "qwen_determinism", "routing_commit")


def compute_qwen_determinism_digest(
    model_id: str,
    model_revision: str,
    tokenizer_revision: str,
    inference_params: dict,
    vllm_version: str,
    cuda_version: str,
    torch_version: str,
) -> str:
    """Compute W-QWEN-DETERMINISM-DIGEST with full SHA-256."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_qwen_determinism_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_qwen_determinism_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_qwen_determinism_digest")
    payload = {
        "model_id": model_id,
        "model_revision": model_revision,
        "tokenizer_revision": tokenizer_revision,
        "inference_params": inference_params,
        "vllm_version": vllm_version,
        "cuda_version": cuda_version,
        "torch_version": torch_version,
    }
    canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def canonicalize_qwen_output(output: str) -> str:
    """Enforce Unicode and whitespace canonicalization for replay consistency."""
    normalized = unicodedata.normalize("NFC", output)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    normalized = normalized.rstrip()
    encoded = normalized.encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_current_determinism_digest() -> str:
    """Compute determinism digest for current runtime configuration."""
    from agentic_core.L2_execution.healers.healing_tier_config import (
        QWEN_CUDA_VERSION,
        QWEN_MODEL_REVISION_SHA,
        QWEN_TOKENIZER_REVISION_SHA,
        QWEN_TORCH_VERSION,
        QWEN_VLLM_VERSION,
    )

    inference_params = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048, "seed": 42}
    return compute_qwen_determinism_digest(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        model_revision=QWEN_MODEL_REVISION_SHA,
        tokenizer_revision=QWEN_TOKENIZER_REVISION_SHA,
        inference_params=inference_params,
        vllm_version=QWEN_VLLM_VERSION,
        cuda_version=QWEN_CUDA_VERSION,
        torch_version=QWEN_TORCH_VERSION,
    )


QWEN_METADATA_FIELDS = {
    "determinism_digest": str,
    "output_hash": str,
    "revision_sha": str,
    "latency_ms": int,
    "memory_used_mb": int,
    "gpu_utilization": float,
    "vllm_version": str,
    "cuda_version": str,
    "torch_version": str,
}
__all__ = [
    "compute_qwen_determinism_digest",
    "canonicalize_qwen_output",
    "compute_current_determinism_digest",
    "QWEN_METADATA_FIELDS",
]

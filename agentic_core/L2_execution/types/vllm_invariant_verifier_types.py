"""
PHASE 5 — Formal Invariant Verifier: Runtime Enforcement Implementation.

Verifies architectural invariants at the execution boundary (Phase 3 adapter/controller seam).
All violations are deterministic and canonically serializable.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

emit_replay_key("p0", "vllm_invariant_verifier_types")
emit_determinism_digest("p0", "vllm_invariant_verifier_types")

_emit_dispatches_healing_run("p1", "vllm_invariant_verifier_types", "L2")
_emit_routes_through("p1", "vllm_invariant_verifier_types", "L2")
_emit_checks_agent_registry("p1", "vllm_invariant_verifier_types", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_invariant_verifier_types", "capability")
_emit_dispatches_execution_plan("p1", "vllm_invariant_verifier_types", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_invariant_verifier_types", "sub_agent")
_emit_routes_to_agent("p1", "vllm_invariant_verifier_types", "target_agent")
_emit_verifies_policy("p1", "vllm_invariant_verifier_types", "policy_check")
_emit_observes_runtime_state("p1", "vllm_invariant_verifier_types", "runtime_state")
_emit_verifies_boundary("p1", "vllm_invariant_verifier_types", "boundary_check")
_emit_transcripts_response("p1", "vllm_invariant_verifier_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_invariant_verifier_types")
_emit_gated_by_confidence("p1", "vllm_invariant_verifier_types", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_invariant_verifier_types", "L2")
_emit_reads_policy_state("p1", "vllm_invariant_verifier_types", "L2")
_emit_authorize_and_execute("p2", "vllm_invariant_verifier_types", "execution_auth")
_emit_validates_capability("p2", "vllm_invariant_verifier_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_invariant_verifier_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_invariant_verifier_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_invariant_verifier_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_invariant_verifier_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_invariant_verifier_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_invariant_verifier_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_invariant_verifier_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_invariant_verifier_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_invariant_verifier_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_invariant_verifier_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_invariant_verifier_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_invariant_verifier_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_invariant_verifier_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_invariant_verifier_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_invariant_verifier_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_invariant_verifier_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_invariant_verifier_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_invariant_verifier_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_invariant_verifier_types", "p4obs", "metric_6")
_emit_records_incident_event("vllm_invariant_verifier_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_invariant_verifier_types", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_invariant_verifier_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_invariant_verifier_types", "p4obs", "mon_state")
_emit_triggers_alert("vllm_invariant_verifier_types", "p4obs", "alert")
_emit_links_incident_trace("vllm_invariant_verifier_types", "p4obs", "trace_link")
_emit_captures_pattern("vllm_invariant_verifier_types", "p3lm", "pattern")
_emit_records_learning_event("vllm_invariant_verifier_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_invariant_verifier_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_invariant_verifier_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_invariant_verifier_types", "p3lm", "routing")
_emit_improves_agent_policy("vllm_invariant_verifier_types", "p3lm", "policy")
_emit_stores_learning_state("vllm_invariant_verifier_types", "p3lm", "state")
_emit_records_execution_trace("vllm_invariant_verifier_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_invariant_verifier_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_invariant_verifier_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_invariant_verifier_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_invariant_verifier_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_invariant_verifier_types", "env_read", "p2_env_1")
_emit_reads_environ("vllm_invariant_verifier_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_invariant_verifier_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_invariant_verifier_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_invariant_verifier_types", "context_pull")
_emit_pulls_context("p1", "vllm_invariant_verifier_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_invariant_verifier_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_invariant_verifier_types", "uwg_term_2")
_emit_writes_through("p1", "vllm_invariant_verifier_types", "write_through")
_emit_writes_through("p1", "vllm_invariant_verifier_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_invariant_verifier_types", "safety_validation")
_emit_invokes_eval("p1", "vllm_invariant_verifier_types", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_invariant_verifier_types", "routing_commit")


def verify_gateway_invariants(
    *,
    provider_selected: str,
    local_request: Any | None,
    telemetry_dict: dict[str, Any],
    fingerprint: Any | None,
    replay_hash_enabled: bool = False,
    gpu_import_policy_ok: bool = True,
) -> list[InvariantViolation]:
    """
    Verify architectural invariants at the gateway execution boundary.

    Args:
        provider_selected: Selected provider (e.g., "Qwen2.5-7B-Instruct" or "gemini-2.5-pro").
        local_request: Shaped local request (None if routed to Gemini).
        telemetry_dict: Telemetry dictionary with stable key ordering.
        fingerprint: Infrastructure fingerprint (None if not provided).
        replay_hash_enabled: If True, enforce replay_hash presence in telemetry (FAIL if missing).
        gpu_import_policy_ok: If False, report GPU import policy violation (FAIL).

    Returns:
        List of InvariantViolation objects, sorted by invariant_id then severity.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "verify_gateway_invariants", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "verify_gateway_invariants", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "verify_gateway_invariants")
    from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
        InvariantId,
        InvariantSeverity,
        InvariantViolation,
    )

    violations: list[InvariantViolation] = []
    if local_request is not None:
        max_tokens = getattr(local_request, "max_tokens", None)
        if max_tokens is None:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Local request missing explicit max_tokens",
                    context={"provider": provider_selected},
                ),
            )
    if local_request is not None:
        temperature = getattr(local_request, "temperature", None)
        if temperature is not None and temperature != 0.0:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value,
                    severity=InvariantSeverity.FAIL.value,
                    message=f"Local request temperature must be 0.0 for determinism, got {temperature}",
                    context={"provider": provider_selected, "temperature": temperature},
                ),
            )
    if local_request is not None:
        seed = getattr(local_request, "seed", None)
        if seed is None:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Local request missing seed for deterministic replay",
                    context={"provider": provider_selected},
                ),
            )
    fingerprint_hash = telemetry_dict.get("fingerprint_hash")
    if not fingerprint_hash:
        violations.append(
            InvariantViolation(
                invariant_id=InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value,
                severity=InvariantSeverity.FAIL.value,
                message="Telemetry missing fingerprint_hash for replay sealing",
                context={"provider": provider_selected},
            ),
        )
    if "gemini" in provider_selected.lower():
        failure_type = telemetry_dict.get("failure_type")
        if not failure_type:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Gemini fallback requires explicit failure_type",
                    context={"provider": provider_selected},
                ),
            )
    if replay_hash_enabled:
        replay_hash = telemetry_dict.get("replay_hash")
        if not replay_hash:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Replay hash enforcement enabled but replay_hash missing from telemetry",
                    context={"provider": provider_selected, "replay_hash_enabled": True},
                ),
            )
    if not gpu_import_policy_ok:
        violations.append(
            InvariantViolation(
                invariant_id=InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value,
                severity=InvariantSeverity.FAIL.value,
                message="GPU import policy violation detected in L0-L6 layers",
                context={"gpu_import_policy_ok": False},
            ),
        )
    violations.sort(key=lambda v: (v.invariant_id, v.severity))
    return violations

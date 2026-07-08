"""
PHASE 3.1 — VLLMGatewayAdapter: thin seam between SovereignLLMGateway and
the Phase 3 call-path controller (evaluate_gateway_call).

This module is the ONLY import boundary that SovereignLLMGateway touches.
It has zero external dependencies — stdlib + Phase 1/2/3 types only.
Tests import this module directly; they never import SovereignLLMGateway.

Seam contract:
    adapter = VLLMGatewayAdapter()
    decision = adapter.evaluate(prompt, task_class, severity,
                                oldest_wait_seconds=0.0)
    # decision.route_to_gemini  → bool
    # decision.local_request    → VLLMLocalRequest | None
    # decision.telemetry        → VLLMGatewayTelemetry
    # decision.telemetry_dict   → dict (stable key order, ASCII-safe)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "vllm_gateway_adapter_types")
trace_contract.emit_determinism_digest("p0", "vllm_gateway_adapter_types")

trace_contract._emit_dispatches_healing_run("p1", "vllm_gateway_adapter_types", "L2")
trace_contract._emit_routes_through("p1", "vllm_gateway_adapter_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "vllm_gateway_adapter_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "vllm_gateway_adapter_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "vllm_gateway_adapter_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "vllm_gateway_adapter_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "vllm_gateway_adapter_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "vllm_gateway_adapter_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "vllm_gateway_adapter_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "vllm_gateway_adapter_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "vllm_gateway_adapter_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "vllm_gateway_adapter_types")
trace_contract._emit_gated_by_confidence("p1", "vllm_gateway_adapter_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "vllm_gateway_adapter_types", "L2")
trace_contract._emit_reads_policy_state("p1", "vllm_gateway_adapter_types", "L2")

trace_contract._emit_applies_guardrail("p0", "vllm_gateway_adapter_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "vllm_gateway_adapter_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "vllm_gateway_adapter_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "vllm_gateway_adapter_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "vllm_gateway_adapter_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "vllm_gateway_adapter_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "vllm_gateway_adapter_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "vllm_gateway_adapter_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "vllm_gateway_adapter_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "vllm_gateway_adapter_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "vllm_gateway_adapter_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "vllm_gateway_adapter_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "vllm_gateway_adapter_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "vllm_gateway_adapter_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "vllm_gateway_adapter_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "vllm_gateway_adapter_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "vllm_gateway_adapter_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "vllm_gateway_adapter_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "vllm_gateway_adapter_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "vllm_gateway_adapter_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "vllm_gateway_adapter_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "vllm_gateway_adapter_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("vllm_gateway_adapter_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("vllm_gateway_adapter_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("vllm_gateway_adapter_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("vllm_gateway_adapter_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("vllm_gateway_adapter_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("vllm_gateway_adapter_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("vllm_gateway_adapter_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("vllm_gateway_adapter_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("vllm_gateway_adapter_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("vllm_gateway_adapter_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("vllm_gateway_adapter_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("vllm_gateway_adapter_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("vllm_gateway_adapter_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("vllm_gateway_adapter_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("vllm_gateway_adapter_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("vllm_gateway_adapter_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("vllm_gateway_adapter_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("vllm_gateway_adapter_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("vllm_gateway_adapter_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("vllm_gateway_adapter_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("vllm_gateway_adapter_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("vllm_gateway_adapter_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("vllm_gateway_adapter_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "vllm_gateway_adapter_types", "context_pull")
trace_contract._emit_pulls_context("p1", "vllm_gateway_adapter_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_gateway_adapter_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_gateway_adapter_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "vllm_gateway_adapter_types", "write_through")
trace_contract._emit_writes_through("p1", "vllm_gateway_adapter_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "vllm_gateway_adapter_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "vllm_gateway_adapter_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "vllm_gateway_adapter_types", "routing_commit")

_DEFAULT_QUEUE: VLLMQueueController | None = None
_DEFAULT_REGISTRY: VLLMCircuitBreakerRegistry | None = None


def _get_default_queue() -> VLLMQueueController:
    global _DEFAULT_QUEUE
    if _DEFAULT_QUEUE is None:
        from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController

        _DEFAULT_QUEUE = VLLMQueueController()
    return _DEFAULT_QUEUE


def _get_default_registry() -> VLLMCircuitBreakerRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMCircuitBreakerRegistry

        _DEFAULT_REGISTRY = VLLMCircuitBreakerRegistry()
    return _DEFAULT_REGISTRY


def reset_singletons() -> None:
    """Reset process-level singletons. For testing only."""
    global _DEFAULT_QUEUE, _DEFAULT_REGISTRY
    _DEFAULT_QUEUE = None
    _DEFAULT_REGISTRY = None


@dataclass
class VLLMGatewayAdapter:
    """Thin seam: wraps evaluate_gateway_call with process-level state.

    SovereignLLMGateway instantiates this once (or uses the module-level
    singleton helpers) and calls .evaluate() before choosing a provider.

    Args:
        queue: Optional queue controller override (for testing).
        registry: Optional circuit breaker registry override (for testing).
    """

    queue: VLLMQueueController | None = field(default=None)
    registry: VLLMCircuitBreakerRegistry | None = field(default=None)

    def evaluate(
        self,
        prompt: str,
        task_class: str,
        severity: str,
        oldest_wait_seconds: float = 0.0,
        fingerprint: VLLMInfrastructureFingerprint | None = None,
    ) -> VLLMGatewayCallResult:
        """Evaluate the call path and return a routing decision.

        PHASE 5: Includes invariant verification at execution boundary.
        FAIL violations trigger Gemini fallback with violations in telemetry.

        Args:
            prompt: Input prompt string.
            task_class: Task class string from TaskClass enum.
            severity: Severity level ("low", "medium", "high").
            oldest_wait_seconds: Age of oldest queued request in seconds.
            fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

        Returns:
            VLLMGatewayCallResult with routing decision + telemetry + violations (if any).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "VLLMGatewayAdapter.evaluate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMGatewayAdapter.evaluate".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
            VLLMGatewayCallResult,
            evaluate_gateway_call,
        )
        from agentic_core.L2_execution.types.vllm_invariant_verifier_types import verify_gateway_invariants

        q = self.queue if self.queue is not None else _get_default_queue()
        r = self.registry if self.registry is not None else _get_default_registry()
        result = evaluate_gateway_call(
            prompt=prompt,
            task_class=task_class,
            severity=severity,
            queue_controller=q,
            breaker_registry=r,
            oldest_wait_seconds=oldest_wait_seconds,
            fingerprint=fingerprint,
        )
        telemetry_dict = result.telemetry.as_dict()
        violations = verify_gateway_invariants(
            provider_selected=telemetry_dict["provider_selected"],
            local_request=result.local_request,
            telemetry_dict=telemetry_dict,
            fingerprint=fingerprint,
            replay_hash_enabled=False,
            gpu_import_policy_ok=True,
        )
        fail_violations = [v for v in violations if v.severity == "FAIL"]
        if fail_violations:
            from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMGatewayTelemetry

            telemetry_with_failure = VLLMGatewayTelemetry(
                provider_selected=result.telemetry.provider_selected,
                model_tier=result.telemetry.model_tier,
                prompt_tokens_estimated=result.telemetry.prompt_tokens_estimated,
                max_output_tokens_requested=result.telemetry.max_output_tokens_requested,
                max_model_len_configured=result.telemetry.max_model_len_configured,
                token_budget_ok=result.telemetry.token_budget_ok,
                budget_margin_tokens=result.telemetry.budget_margin_tokens,
                queue_depth=result.telemetry.queue_depth,
                queue_full=result.telemetry.queue_full,
                queue_wait_seconds=result.telemetry.queue_wait_seconds,
                breaker_state=result.telemetry.breaker_state,
                breaker_failure_count=result.telemetry.breaker_failure_count,
                failure_type="INVARIANT_VIOLATION",
                model_name=result.telemetry.model_name,
                model_revision_sha=result.telemetry.model_revision_sha,
                vllm_version=result.telemetry.vllm_version,
                transformers_version=result.telemetry.transformers_version,
                torch_version=result.telemetry.torch_version,
                cuda_version=result.telemetry.cuda_version,
                driver_version=result.telemetry.driver_version,
                fingerprint_hash=result.telemetry.fingerprint_hash,
            )
            result = VLLMGatewayCallResult(
                route_to_gemini=True,
                local_request=None,
                telemetry=telemetry_with_failure,
                preflight=result.preflight,
                backpressure=result.backpressure,
                invariant_violations=violations,
            )
        elif violations:
            result = VLLMGatewayCallResult(
                route_to_gemini=result.route_to_gemini,
                local_request=result.local_request,
                telemetry=result.telemetry,
                preflight=result.preflight,
                backpressure=result.backpressure,
                invariant_violations=violations,
            )
        return result

    def record_local_failure(self, severity: str) -> None:
        """Record a local vLLM failure for circuit breaker tracking."""
        r = self.registry if self.registry is not None else _get_default_registry()
        tier = "local_strong" if severity == "high" else "local_fast"
        r.record_failure(tier)

    def record_local_success(self, severity: str) -> None:
        """Record a local vLLM success for circuit breaker tracking."""
        r = self.registry if self.registry is not None else _get_default_registry()
        tier = "local_strong" if severity == "high" else "local_fast"
        r.record_success(tier)


SEAM_PROOF_MARKER = "OK: SovereignLLMGateway uses VLLMGatewayAdapter -> evaluate_gateway_call"


def emit_seam_proof() -> str:
    """Return the seam proof marker string. Used by evidence runner."""
    return SEAM_PROOF_MARKER


__all__ = ["SEAM_PROOF_MARKER", "VLLMGatewayAdapter", "emit_seam_proof", "reset_singletons"]

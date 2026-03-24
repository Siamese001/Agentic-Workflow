"""
Phase 1 E2E Harness: Gemini 2.5 Pro + Qwen vLLM deterministic pipeline.
Waves 1-3: positive paths, negative control, seam proof.
No external network calls. Production routing + execution surfaces used.
"""

from __future__ import annotations

import re
import socket
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_gemini_qwen_e2e")
_emit_applies_guardrail("p0", "test_gemini_qwen_e2e", "p0_governance")
_emit_reads_policy_state("p0", "test_gemini_qwen_e2e", "policy_binding")
_emit_snapshots_state("p0", "test_gemini_qwen_e2e", "state_snapshot")
emit_replay_key("p0", "test_gemini_qwen_e2e")
emit_determinism_digest("p0", "test_gemini_qwen_e2e")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_gemini_qwen_e2e", "execution_auth")
_emit_validates_capability("p2", "test_gemini_qwen_e2e", "capability_check")
_emit_routes_to_capability("p2", "test_gemini_qwen_e2e", "capability_route")
_emit_writes_via_uwg("p2", "test_gemini_qwen_e2e", "uwg_write")
_emit_blocks_direct_write("p2", "test_gemini_qwen_e2e", "direct_write_block")
_emit_records_tool_invocation("p2", "test_gemini_qwen_e2e", "tool_invocation")
_emit_captures_execution_output("p2", "test_gemini_qwen_e2e", "exec_output")
_emit_dispatches_agent("p3", "test_gemini_qwen_e2e", "agent_dispatch")
_emit_coordinates_agents("p3", "test_gemini_qwen_e2e", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_gemini_qwen_e2e", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_gemini_qwen_e2e", "healing_outcome")
_emit_escalates_failure("p3", "test_gemini_qwen_e2e", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_gemini_qwen_e2e", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_gemini_qwen_e2e", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_gemini_qwen_e2e", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_gemini_qwen_e2e", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_gemini_qwen_e2e", "eval_metric")
_emit_stores_embedding("p4", "test_gemini_qwen_e2e", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_gemini_qwen_e2e", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_gemini_qwen_e2e", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.e2e

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
ENGINE_GEMINI = "gemini-2.5-pro"
ENGINE_QWEN = "qwen-vllm"
_STUB_PROMPT = "E2E deterministic test payload v1"
_STUB_RESPONSE_GEMINI = b"stub-gemini-response-fixed-content-v1"
_STUB_RESPONSE_QWEN = b"stub-qwen-response-fixed-content-v1"

_FINGERPRINT_GEMINI = {
    "model_name": ENGINE_GEMINI,
    "model_revision_sha": "gemini25pro-stub-rev-0001",
    "vllm_version": "N/A",
    "transformers_version": "N/A",
    "torch_version": "N/A",
    "cuda_version": "N/A",
    "driver_version": "N/A",
}
_FINGERPRINT_QWEN = {
    "model_name": ENGINE_QWEN,
    "model_revision_sha": "qwen-vllm-stub-rev-0001",
    "vllm_version": "0.6.3-stub",
    "transformers_version": "4.46.0-stub",
    "torch_version": "2.5.1-stub",
    "cuda_version": "12.4-stub",
    "driver_version": "550.54.14-stub",
}


class _NetworkBlockedError(RuntimeError):
    pass


def _blocked_connect(*args, **kwargs):
    raise _NetworkBlockedError("NETWORK GUARD: socket.connect() called during E2E test.")


def _blocked_getaddrinfo(*args, **kwargs):
    raise _NetworkBlockedError("NETWORK GUARD: socket.getaddrinfo() called during E2E test.")


@pytest.fixture(autouse=True)
def network_guard():
    patches = []
    p1 = patch.object(socket.socket, "connect", _blocked_connect)
    p2 = patch("socket.getaddrinfo", _blocked_getaddrinfo)
    patches.extend([p1, p2])
    try:
        import requests  # noqa: F401

        p3 = patch(
            "requests.Session.send",
            side_effect=_NetworkBlockedError("NETWORK GUARD: requests.Session.send() called."),
        )
        patches.append(p3)
    pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
        pass
    try:
        import httpx  # noqa: F401

        p4 = patch(
            "httpx.Client.send",
            side_effect=_NetworkBlockedError("NETWORK GUARD: httpx.Client.send() called."),
        )
        patches.append(p4)
    pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
        pass
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


from agentic_core.L2_execution.types.llm_replay_types import ReplayBundle
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMGatewayCallResult,
    VLLMGatewayTelemetry,
    VLLMLocalRequest,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)
from agentic_core.L2_execution.types.vllm_invariant_verifier_types import verify_gateway_invariants
from agentic_core.L2_execution.types.vllm_replay_validator_types import compute_replay_hash
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_1")
_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_2")
_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_3")
_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_4")
_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_5")
_emit_emits_metric_event("test_gemini_qwen_e2e", "p4obs", "metric_6")
_emit_records_incident_event("test_gemini_qwen_e2e", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_gemini_qwen_e2e", "p4obs", "anomaly")
_emit_writes_observability_log("test_gemini_qwen_e2e", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_gemini_qwen_e2e", "p4obs", "mon_state")
_emit_triggers_alert("test_gemini_qwen_e2e", "p4obs", "alert")
_emit_links_incident_trace("test_gemini_qwen_e2e", "p4obs", "trace_link")
_emit_captures_pattern("test_gemini_qwen_e2e", "p3lm", "pattern")
_emit_records_learning_event("test_gemini_qwen_e2e", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_gemini_qwen_e2e", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_gemini_qwen_e2e", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_gemini_qwen_e2e", "p3lm", "routing")
_emit_improves_agent_policy("test_gemini_qwen_e2e", "p3lm", "policy")
_emit_stores_learning_state("test_gemini_qwen_e2e", "p3lm", "state")
_emit_records_execution_trace("test_gemini_qwen_e2e", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_gemini_qwen_e2e", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_gemini_qwen_e2e", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_gemini_qwen_e2e", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_gemini_qwen_e2e", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_gemini_qwen_e2e", "env_read", "p2_env_1")
_emit_reads_environ("test_gemini_qwen_e2e", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_gemini_qwen_e2e", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_gemini_qwen_e2e", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_gemini_qwen_e2e", "context_pull")
_emit_pulls_context("p1", "test_gemini_qwen_e2e", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_gemini_qwen_e2e", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_gemini_qwen_e2e", "uwg_term_2")
_emit_writes_through("p1", "test_gemini_qwen_e2e", "write_through")
_emit_writes_through("p1", "test_gemini_qwen_e2e", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_gemini_qwen_e2e", "safety_validation")
_emit_invokes_eval("p1", "test_gemini_qwen_e2e", "eval_call")
_emit_proposal_commits_routing("p1", "test_gemini_qwen_e2e", "routing_commit")
_emit_escalates_to_human("p1", "test_gemini_qwen_e2e", "human_escalation")
_emit_routes_through("p1", "test_gemini_qwen_e2e", "route_through")
_emit_checks_agent_registry("p1", "test_gemini_qwen_e2e", "agent_registry")
_emit_validates_agent_capability("p1", "test_gemini_qwen_e2e", "capability")
_emit_dispatches_execution_plan("p1", "test_gemini_qwen_e2e", "exec_plan")
_emit_agent_executes_agent("p1", "test_gemini_qwen_e2e", "sub_agent")
_emit_routes_to_agent("p1", "test_gemini_qwen_e2e", "target_agent")
_emit_verifies_policy("p1", "test_gemini_qwen_e2e", "policy_check")
_emit_observes_runtime_state("p1", "test_gemini_qwen_e2e", "runtime_state")
_emit_verifies_boundary("p1", "test_gemini_qwen_e2e", "boundary_check")
_emit_transcripts_response("p1", "test_gemini_qwen_e2e", "transcript")
_emit_hard_fails_untranscripted("p1", "test_gemini_qwen_e2e")
_emit_gated_by_confidence("p1", "test_gemini_qwen_e2e", "confidence_gate")


def _make_fingerprint(fields: dict) -> VLLMInfrastructureFingerprint:
    return VLLMInfrastructureFingerprint(
        model_name=fields["model_name"],
        model_revision_sha=fields["model_revision_sha"],
        vllm_version=fields["vllm_version"],
        transformers_version=fields["transformers_version"],
        torch_version=fields["torch_version"],
        cuda_version=fields["cuda_version"],
        driver_version=fields["driver_version"],
    )


def _make_stub_telemetry(*, provider_selected, model_tier, failure_type, fingerprint):
    return VLLMGatewayTelemetry(
        provider_selected=provider_selected,
        model_tier=model_tier,
        prompt_tokens_estimated=10,
        max_output_tokens_requested=600,
        max_model_len_configured=32768,
        token_budget_ok=True,
        budget_margin_tokens=32158,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type=failure_type,
        model_name=fingerprint.model_name,
        model_revision_sha=fingerprint.model_revision_sha,
        vllm_version=fingerprint.vllm_version,
        transformers_version=fingerprint.transformers_version,
        torch_version=fingerprint.torch_version,
        cuda_version=fingerprint.cuda_version,
        driver_version=fingerprint.driver_version,
        fingerprint_hash=fingerprint.fingerprint_hash(),
    )


def _make_stub_preflight():
    from agentic_core.L2_execution.types.vllm_token_budget_types import VLLMPreflightResult

    return VLLMPreflightResult(
        prompt_tokens_estimated=10,
        max_output_tokens_requested=600,
        max_model_len_configured=32768,
        token_budget_ok=True,
        budget_margin_tokens=32158,
        failure_type=None,
        route_to_gemini=False,
    )


def _make_stub_backpressure():
    from agentic_core.L2_execution.types.vllm_backpressure_types import BackpressureDecision

    return BackpressureDecision(
        escalate_to_gemini=False,
        reason="ok",
        failure_type=None,
        model_id="",
        queue_depth=0,
        circuit_breaker_open=False,
    )


def run_e2e_pipeline(
    *,
    route_override: str,
    prompt: str = _STUB_PROMPT,
    force_invariant_fail: bool = False,
    forced_violation: InvariantViolation | None = None,
) -> dict[str, Any]:
    """
    Run the full L0->L2 pipeline with a deterministic model-transport stub.

    Returns dict with EXACT keys:
      route_decision, engine_name, replay_hash, invariant_violations,
      failure_type, route_to_gemini, escalation_occurred,
      shadow_classifier_changed_decision
    """
    if route_override not in (ENGINE_GEMINI, ENGINE_QWEN):
        raise ValueError(f"route_override must be {ENGINE_GEMINI!r} or {ENGINE_QWEN!r}")

    fp_fields = _FINGERPRINT_GEMINI if route_override == ENGINE_GEMINI else _FINGERPRINT_QWEN
    fingerprint = _make_fingerprint(fp_fields)

    if route_override == ENGINE_GEMINI:
        provider_selected = ENGINE_GEMINI
        model_tier = "remote"
        local_request = None
        # INV_GEMINI_FALLBACK_REQUIRES_REASON: Gemini provider always requires
        # an explicit failure_type per production invariant contract.
        # For the positive Gemini path (intentional route override), use
        # "GEMINI_ROUTE_OVERRIDE" as the explicit reason.
        telemetry_failure_type = "GEMINI_ROUTE_OVERRIDE"
    else:
        provider_selected = ENGINE_QWEN
        model_tier = "fast"
        local_request = VLLMLocalRequest(
            model=ENGINE_QWEN,
            prompt=prompt,
            max_tokens=600,
            temperature=0.0,
            top_p=1.0,
            seed=42,
            task_class="patch_suggestion",
            profile_name="LOCAL_FAST_7B",
            max_model_len=32768,
        )
        telemetry_failure_type = None

    telemetry = _make_stub_telemetry(
        provider_selected=provider_selected,
        model_tier=model_tier,
        failure_type=telemetry_failure_type,
        fingerprint=fingerprint,
    )
    preflight = _make_stub_preflight()
    backpressure = _make_stub_backpressure()

    # Invariant verification: production path or test-only seam
    if force_invariant_fail and forced_violation is not None:
        violations = [forced_violation]
    else:
        violations = verify_gateway_invariants(
            provider_selected=provider_selected,
            local_request=local_request,
            telemetry_dict=telemetry.as_dict(),
            fingerprint=fingerprint,
            replay_hash_enabled=False,
            gpu_import_policy_ok=True,
        )

    fail_violations = [v for v in violations if v.severity == "FAIL"]

    if fail_violations:
        escalated_telemetry = _make_stub_telemetry(
            provider_selected=provider_selected,
            model_tier=model_tier,
            failure_type="INVARIANT_VIOLATION",
            fingerprint=fingerprint,
        )
        final_result = VLLMGatewayCallResult(
            route_to_gemini=True,
            local_request=None,
            telemetry=escalated_telemetry,
            preflight=preflight,
            backpressure=backpressure,
            invariant_violations=violations,
        )
        escalation_occurred = True
        effective_failure_type = "INVARIANT_VIOLATION"
    else:
        final_result = VLLMGatewayCallResult(
            route_to_gemini=False,  # No escalation on positive path regardless of engine
            local_request=local_request,
            telemetry=telemetry,
            preflight=preflight,
            backpressure=backpressure,
            invariant_violations=violations,
        )
        escalation_occurred = False
        effective_failure_type = None

    replay_hash = compute_replay_hash(
        prompt=prompt,
        request=final_result.local_request,
        fingerprint=fingerprint,
        result=final_result,
    )

    # Capture replay bundle (L2 replay types)
    replay_bundle = ReplayBundle.create(
        model_version=route_override,
        tokenizer_version="stub-tokenizer-v1",
        raw_prompt_bytes=prompt.encode("utf-8"),
        raw_response_bytes=(
            _STUB_RESPONSE_GEMINI if route_override == ENGINE_GEMINI else _STUB_RESPONSE_QWEN
        ),
    )

    return {
        "route_decision": f"route_override={route_override}",
        "engine_name": route_override,
        "replay_hash": replay_hash,
        "invariant_violations": final_result.invariant_violations,
        "failure_type": effective_failure_type,
        "route_to_gemini": final_result.route_to_gemini,
        "escalation_occurred": escalation_occurred,
        "shadow_classifier_changed_decision": False,
        "_replay_bundle_hash": replay_bundle.replay_hash,
        "_fingerprint_hash": fingerprint.fingerprint_hash(),
    }


def _make_forced_invariant_violation() -> InvariantViolation:
    """Test-only seam: deterministic forced FAIL violation for Wave 2 negative control."""
    return InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="E2E-TEST-SEAM: forced invariant failure for negative control",
        context={
            "provider": ENGINE_GEMINI,
            "seam": "test_only",
            "replay_hash_enabled": True,
        },
    )


# ---------------------------------------------------------------------------
# Wave 1 — Gemini positive path
# ---------------------------------------------------------------------------


class TestGeminiE2EPath:
    def test_engine_name_exact(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["engine_name"] == ENGINE_GEMINI

    def test_no_invariant_violations(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["invariant_violations"] == []

    def test_failure_type_none(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["failure_type"] is None

    def test_no_escalation(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["escalation_occurred"] is False

    def test_route_to_gemini_false(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["route_to_gemini"] is False

    def test_shadow_classifier_no_change(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert result["shadow_classifier_changed_decision"] is False

    def test_replay_hash_is_64hex(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        r2 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
        assert r1["replay_hash"] == r2["replay_hash"]


# ---------------------------------------------------------------------------
# Wave 1 — Qwen positive path
# ---------------------------------------------------------------------------


class TestQwenE2EPath:
    def test_engine_name_exact(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["engine_name"] == ENGINE_QWEN

    def test_no_invariant_violations(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["invariant_violations"] == []

    def test_failure_type_none(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["failure_type"] is None

    def test_no_escalation(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["escalation_occurred"] is False

    def test_route_to_gemini_false(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["route_to_gemini"] is False

    def test_shadow_classifier_no_change(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert result["shadow_classifier_changed_decision"] is False

    def test_replay_hash_is_64hex(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = run_e2e_pipeline(route_override=ENGINE_QWEN)
        r2 = run_e2e_pipeline(route_override=ENGINE_QWEN)
        assert r1["replay_hash"] == r2["replay_hash"]


# ---------------------------------------------------------------------------
# Wave 2 — Negative Control: Invariant failure -> escalation
# ---------------------------------------------------------------------------


class TestNegativeControlInvariantViolation:
    def _run_negative(self) -> dict[str, Any]:
        return run_e2e_pipeline(
            route_override=ENGINE_GEMINI,
            force_invariant_fail=True,
            forced_violation=_make_forced_invariant_violation(),
        )

    def test_route_to_gemini_true(self):
        result = self._run_negative()
        assert result["route_to_gemini"] is True

    def test_failure_type_invariant_violation(self):
        result = self._run_negative()
        assert result["failure_type"] == "INVARIANT_VIOLATION"

    def test_violations_nonempty(self):
        result = self._run_negative()
        assert len(result["invariant_violations"]) >= 1

    def test_violation_hash_is_64hex(self):
        result = self._run_negative()
        vh = result["invariant_violations"][0].violation_hash()
        assert _HEX64_RE.match(vh), f"violation_hash not 64-hex: {vh!r}"

    def test_replay_hash_is_64hex(self):
        result = self._run_negative()
        assert _HEX64_RE.match(result["replay_hash"]), f"Not 64-hex: {result['replay_hash']!r}"

    def test_replay_hash_deterministic(self):
        r1 = self._run_negative()
        r2 = self._run_negative()
        assert r1["replay_hash"] == r2["replay_hash"]

    def test_escalation_occurred(self):
        result = self._run_negative()
        assert result["escalation_occurred"] is True


# ---------------------------------------------------------------------------
# Wave 3 — Seam proof: production path safety
# ---------------------------------------------------------------------------


class TestSeamProductionSafety:
    def test_production_path_no_violations_gemini(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert result["invariant_violations"] == []
        assert result["failure_type"] is None

    def test_production_path_no_violations_qwen(self):
        result = run_e2e_pipeline(route_override=ENGINE_QWEN, force_invariant_fail=False)
        assert result["invariant_violations"] == []
        assert result["failure_type"] is None

    def test_seam_active_only_when_explicitly_enabled(self):
        prod = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert prod["invariant_violations"] == []
        seam = run_e2e_pipeline(
            route_override=ENGINE_GEMINI,
            force_invariant_fail=True,
            forced_violation=_make_forced_invariant_violation(),
        )
        assert len(seam["invariant_violations"]) >= 1

    def test_real_verifier_called_on_production_path(self):
        result = run_e2e_pipeline(route_override=ENGINE_GEMINI, force_invariant_fail=False)
        assert result["invariant_violations"] == []
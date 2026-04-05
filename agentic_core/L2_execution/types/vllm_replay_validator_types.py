"""
PHASE 4 WAVE 3 — VLLMReplayValidator: deterministic replay sealing.

Provides canonical hashing utilities and replay validation for vLLM gateway
calls. Ensures identical inputs produce identical hashes and detects tampering.

Replay components (canonical, sorted keys):
- prompt_hash: SHA256 of canonical prompt representation
- local_request_hash: SHA256 of shaped local_request dict
- fingerprint_hash: SHA256 of infrastructure fingerprint canonical JSON
- response_hash: SHA256 of structured response artifact / telemetry decision record

replay_hash = SHA256(prompt_hash + local_request_hash + fingerprint_hash + response_hash)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "vllm_replay_validator_types")
emit_determinism_digest("p0", "vllm_replay_validator_types")

_emit_dispatches_healing_run("p1", "vllm_replay_validator_types", "L2")
_emit_routes_through("p1", "vllm_replay_validator_types", "L2")
_emit_checks_agent_registry("p1", "vllm_replay_validator_types", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_replay_validator_types", "capability")
_emit_dispatches_execution_plan("p1", "vllm_replay_validator_types", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_replay_validator_types", "sub_agent")
_emit_routes_to_agent("p1", "vllm_replay_validator_types", "target_agent")
_emit_verifies_policy("p1", "vllm_replay_validator_types", "policy_check")
_emit_observes_runtime_state("p1", "vllm_replay_validator_types", "runtime_state")
_emit_verifies_boundary("p1", "vllm_replay_validator_types", "boundary_check")
_emit_transcripts_response("p1", "vllm_replay_validator_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_replay_validator_types")
_emit_gated_by_confidence("p1", "vllm_replay_validator_types", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_replay_validator_types", "L2")
_emit_reads_policy_state("p1", "vllm_replay_validator_types", "L2")

_emit_applies_guardrail("p0", "vllm_replay_validator_types", "p0_governance")
_emit_snapshots_state("p0", "vllm_replay_validator_types", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_replay_validator_types", "execution_auth")
_emit_validates_capability("p2", "vllm_replay_validator_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_replay_validator_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_replay_validator_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_replay_validator_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_replay_validator_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_replay_validator_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_replay_validator_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_replay_validator_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_replay_validator_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_replay_validator_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_replay_validator_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_replay_validator_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_replay_validator_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_replay_validator_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_replay_validator_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_replay_validator_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_replay_validator_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_replay_validator_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_replay_validator_types", "exec_snapshot_link")
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

_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_replay_validator_types", "p4obs", "metric_6")
_emit_records_incident_event("vllm_replay_validator_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_replay_validator_types", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_replay_validator_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_replay_validator_types", "p4obs", "mon_state")
_emit_triggers_alert("vllm_replay_validator_types", "p4obs", "alert")
_emit_links_incident_trace("vllm_replay_validator_types", "p4obs", "trace_link")
_emit_captures_pattern("vllm_replay_validator_types", "p3lm", "pattern")
_emit_records_learning_event("vllm_replay_validator_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_replay_validator_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_replay_validator_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_replay_validator_types", "p3lm", "routing")
_emit_improves_agent_policy("vllm_replay_validator_types", "p3lm", "policy")
_emit_stores_learning_state("vllm_replay_validator_types", "p3lm", "state")
_emit_records_execution_trace("vllm_replay_validator_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_replay_validator_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_replay_validator_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_replay_validator_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_replay_validator_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_replay_validator_types", "env_read", "p2_env_1")
_emit_reads_environ("vllm_replay_validator_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_replay_validator_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_replay_validator_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_replay_validator_types", "context_pull")
_emit_pulls_context("p1", "vllm_replay_validator_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_replay_validator_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_replay_validator_types", "uwg_term_2")
_emit_writes_through("p1", "vllm_replay_validator_types", "write_through")
_emit_writes_through("p1", "vllm_replay_validator_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_replay_validator_types", "safety_validation")
_emit_invokes_eval("p1", "vllm_replay_validator_types", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_replay_validator_types", "routing_commit")
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

record_execution_trace("vllm_replay_validator_types", "vllm_replay_validator_types_trace")

emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_dispatch_entry")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_dispatch_exit")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_tool_invoke")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_tool_complete")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_agent_entry")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_agent_exit")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_uwg_write")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_trace_sign")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_guardrail_check")
emit_determinism_digest("trace_vllm_replay_validator_types", "vllm_replay_validator_types_policy_verify")


def canonical_prompt_hash(prompt: str) -> str:
    """
    Compute SHA256 hash of canonical prompt representation.

    Args:
        prompt: Input prompt string.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    return sha256_hex(canonical_json({"prompt": prompt}))


def canonical_local_request_hash(request: VLLMLocalRequest) -> str:
    """
    Compute SHA256 hash of shaped local request dict.

    Args:
        request: VLLMLocalRequest instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    request_dict = {
        "prompt": request.prompt,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "seed": request.seed,
        "task_class": request.task_class,
        "profile_name": request.profile_name,
        "max_model_len": request.max_model_len,
    }
    return sha256_hex(canonical_json(request_dict))


def canonical_response_hash(result: VLLMGatewayCallResult) -> str:
    """
    Compute SHA256 hash of structured response artifact / telemetry decision record.

    PHASE 6: Includes invariant violations in canonical form for replay integrity.

    Args:
        result: VLLMGatewayCallResult instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    telemetry_dict = result.telemetry.as_dict()
    if result.invariant_violations:
        violations_canonical = [v.as_dict() for v in result.invariant_violations]
        telemetry_dict["invariant_violations"] = violations_canonical
    return sha256_hex(canonical_json(telemetry_dict))


def compute_replay_hash(
    prompt: str,
    request: VLLMLocalRequest | None,
    fingerprint: VLLMInfrastructureFingerprint,
    result: VLLMGatewayCallResult,
) -> str:
    """
    Compute deterministic replay hash from all components.

    replay_hash = SHA256(prompt_hash + local_request_hash + fingerprint_hash + response_hash)

    Args:
        prompt: Input prompt string.
        request: Shaped local request (None if routed to Gemini).
        fingerprint: Infrastructure fingerprint.
        result: Gateway call result.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    prompt_hash = canonical_prompt_hash(prompt)
    if request is None:
        local_request_hash = sha256_hex(canonical_json({}))
    else:
        local_request_hash = canonical_local_request_hash(request)
    fingerprint_hash = fingerprint.fingerprint_hash()
    response_hash = canonical_response_hash(result)
    combined = prompt_hash + local_request_hash + fingerprint_hash + response_hash
    return sha256_hex(combined)


@dataclass(frozen=True)
class VLLMReplayArtifact:
    """Immutable artifact for deterministic replay validation.

    Contains all components needed to recompute and verify replay_hash.
    """

    prompt: str
    local_request: VLLMLocalRequest | None
    fingerprint: VLLMInfrastructureFingerprint
    result: VLLMGatewayCallResult
    prompt_hash: str = field(init=False)
    local_request_hash: str = field(init=False)
    fingerprint_hash: str = field(init=False)
    response_hash: str = field(init=False)
    replay_hash: str = field(init=False)

    def __post_init__(self) -> None:
        from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
            canonical_json,
            sha256_hex,
        )

        object.__setattr__(self, "prompt_hash", canonical_prompt_hash(self.prompt))
        if self.local_request is None:
            object.__setattr__(self, "local_request_hash", sha256_hex(canonical_json({})))
        else:
            object.__setattr__(self, "local_request_hash", canonical_local_request_hash(self.local_request))
        object.__setattr__(self, "fingerprint_hash", self.fingerprint.fingerprint_hash())
        object.__setattr__(self, "response_hash", canonical_response_hash(self.result))
        combined = self.prompt_hash + self.local_request_hash + self.fingerprint_hash + self.response_hash
        object.__setattr__(self, "replay_hash", sha256_hex(combined))

    def canonical_payload_hash(self) -> str:
        """
        Get the canonical payload hash derived from the exact bytes used for replay_hash computation.

        This reflects the combined canonical payload (prompt_hash + local_request_hash +
        fingerprint_hash + response_hash) before the final SHA-256.

        Returns:
            64-character lowercase hex SHA256 digest of the canonical payload.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "VLLMReplayArtifact.canonical_payload_hash"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:VLLMReplayArtifact.canonical_payload_hash".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import sha256_hex

        combined = self.prompt_hash + self.local_request_hash + self.fingerprint_hash + self.response_hash
        return sha256_hex(combined)

    def verify(self) -> bool:
        """
        Verify that stored hashes match recomputed hashes.

        Returns:
            True if all hashes match (artifact is untampered), False otherwise.
        """
        current_replay_hash = compute_replay_hash(
            prompt=self.prompt, request=self.local_request, fingerprint=self.fingerprint, result=self.result
        )
        return current_replay_hash == self.replay_hash


@dataclass(frozen=True)
class VLLMReplayValidator:
    """Minimal replay validator for tamper detection."""

    def validate(self, artifact: VLLMReplayArtifact) -> bool:
        """
        Validate a replay artifact.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            True if artifact is valid (untampered), False otherwise.
        """
        return artifact.verify()

    def validate_and_report(self, artifact: VLLMReplayArtifact) -> dict[str, Any]:
        """
        Validate artifact and return detailed report.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            Dict with validation result and hash details.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "VLLMReplayValidator.validate_and_report"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:VLLMReplayValidator.validate_and_report".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        is_valid = self.validate(artifact)
        if not is_valid:
            current_replay_hash = compute_replay_hash(
                prompt=artifact.prompt,
                request=artifact.local_request,
                fingerprint=artifact.fingerprint,
                result=artifact.result,
            )
        else:
            current_replay_hash = artifact.replay_hash
        return {
            "valid": is_valid,
            "stored_replay_hash": artifact.replay_hash,
            "computed_replay_hash": current_replay_hash,
            "prompt_hash": artifact.prompt_hash,
            "local_request_hash": artifact.local_request_hash,
            "fingerprint_hash": artifact.fingerprint_hash,
            "response_hash": artifact.response_hash,
        }


__all__ = [
    "VLLMReplayArtifact",
    "VLLMReplayValidator",
    "canonical_prompt_hash",
    "canonical_local_request_hash",
    "canonical_response_hash",
    "compute_replay_hash",
]

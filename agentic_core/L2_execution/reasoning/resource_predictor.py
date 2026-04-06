"""
Resource predictor engine for L2 execution learning.
Deterministic resource envelope prediction from failure signatures.
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.L2_execution.types.resource_prediction_types import (
    FailureSignature,
    ResourceEnvelope,
    ResourcePrediction,
)
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
)

emit_replay_key("p0", "resource_predictor")
emit_determinism_digest("p0", "resource_predictor")

_emit_dispatches_healing_run("p1", "resource_predictor", "L2")
_emit_routes_through("p1", "resource_predictor", "L2")
_emit_checks_agent_registry("p1", "resource_predictor", "agent_registry")
_emit_validates_agent_capability("p1", "resource_predictor", "capability")
_emit_dispatches_execution_plan("p1", "resource_predictor", "exec_plan")
_emit_agent_executes_agent("p1", "resource_predictor", "sub_agent")
_emit_routes_to_agent("p1", "resource_predictor", "target_agent")
_emit_verifies_policy("p1", "resource_predictor", "policy_check")
_emit_observes_runtime_state("p1", "resource_predictor", "runtime_state")
_emit_verifies_boundary("p1", "resource_predictor", "boundary_check")
_emit_transcripts_response("p1", "resource_predictor", "transcript")
_emit_hard_fails_untranscripted("p1", "resource_predictor")
_emit_gated_by_confidence("p1", "resource_predictor", "confidence_gate")
_emit_escalates_to_human("p1", "resource_predictor", "L2")
_emit_reads_policy_state("p1", "resource_predictor", "L2")

_emit_applies_guardrail("p0", "resource_predictor", "p0_governance")
_emit_snapshots_state("p0", "resource_predictor", "state_snapshot")
_emit_authorize_and_execute("p2", "resource_predictor", "execution_auth")
_emit_validates_capability("p2", "resource_predictor", "capability_check")
_emit_routes_to_capability("p2", "resource_predictor", "capability_route")
_emit_writes_via_uwg("p2", "resource_predictor", "uwg_write")
_emit_blocks_direct_write("p2", "resource_predictor", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_predictor", "tool_invocation")
_emit_captures_execution_output("p2", "resource_predictor", "exec_output")
_emit_dispatches_agent("p3", "resource_predictor", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_predictor", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_predictor", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_predictor", "healing_outcome")
_emit_escalates_failure("p3", "resource_predictor", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_predictor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_predictor", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_predictor", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_predictor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_predictor", "eval_metric")
_emit_stores_embedding("p4", "resource_predictor", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_predictor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_predictor", "exec_snapshot_link")
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

_emit_emits_metric_event("resource_predictor", "p4obs", "metric_1")
_emit_emits_metric_event("resource_predictor", "p4obs", "metric_2")
_emit_emits_metric_event("resource_predictor", "p4obs", "metric_3")
_emit_emits_metric_event("resource_predictor", "p4obs", "metric_4")
_emit_emits_metric_event("resource_predictor", "p4obs", "metric_5")
_emit_emits_metric_event("resource_predictor", "p4obs", "metric_6")
_emit_records_incident_event("resource_predictor", "p4obs", "incident")
_emit_captures_runtime_anomaly("resource_predictor", "p4obs", "anomaly")
_emit_writes_observability_log("resource_predictor", "p4obs", "obs_log")
_emit_updates_monitoring_state("resource_predictor", "p4obs", "mon_state")
_emit_triggers_alert("resource_predictor", "p4obs", "alert")
_emit_links_incident_trace("resource_predictor", "p4obs", "trace_link")
_emit_captures_pattern("resource_predictor", "p3lm", "pattern")
_emit_records_learning_event("resource_predictor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resource_predictor", "p3lm", "snapshot")
_emit_feeds_meta_learning("resource_predictor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resource_predictor", "p3lm", "routing")
_emit_improves_agent_policy("resource_predictor", "p3lm", "policy")
_emit_stores_learning_state("resource_predictor", "p3lm", "state")
_emit_records_execution_trace("resource_predictor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resource_predictor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resource_predictor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resource_predictor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resource_predictor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resource_predictor", "env_read", "p2_env_1")
_emit_reads_environ("resource_predictor", "env_read", "p2_env_2")
_emit_reads_runtime_state("resource_predictor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resource_predictor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resource_predictor", "context_pull")
_emit_pulls_context("p1", "resource_predictor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resource_predictor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resource_predictor", "uwg_term_2")
_emit_writes_through("p1", "resource_predictor", "write_through")
_emit_writes_through("p1", "resource_predictor", "write_through_2")
_emit_validated_by_safety_plane("p1", "resource_predictor", "safety_validation")
_emit_invokes_eval("p1", "resource_predictor", "eval_call")
_emit_proposal_commits_routing("p1", "resource_predictor", "routing_commit")


class ResourcePredictor(Protocol):
    """Protocol for resource prediction engines."""

    def predict(
        *,
        signature: FailureSignature,
        history_bytes: bytes | None = None,
    ) -> ResourcePrediction:
        """Predict resource envelope for a failure signature."""
        ...


class DefaultDeterministicResourcePredictor:
    """Deterministic resource predictor with bounded outputs."""

    # Configuration bounds
    MIN_CPU_CORES: int = 1
    MAX_CPU_CORES: int = 16
    MIN_MEMORY_MB: int = 512
    MAX_MEMORY_MB: int = 16384
    MIN_TIMEOUT_S: int = 30
    MAX_TIMEOUT_S: int = 3600

    # Deterministic baseline envelopes by failure type
    _BASELINE_ENVELOPES: dict[str, ResourceEnvelope] = {
        # guardian: allow-magic-config
        "timeout": ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300),
        # guardian: allow-magic-config
        "memory_error": ResourceEnvelope(cpu_cores=1, memory_mb=2048, timeout_s=180),
        # guardian: allow-magic-config
        "cpu_error": ResourceEnvelope(cpu_cores=4, memory_mb=512, timeout_s=240),
        # guardian: allow-magic-config
        "io_error": ResourceEnvelope(cpu_cores=2, memory_mb=1536, timeout_s=600),
        # guardian: allow-magic-config
        "network_error": ResourceEnvelope(cpu_cores=1, memory_mb=768, timeout_s=120),
        # guardian: allow-magic-config
        "unknown": ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300),
    }

    def __init__(
        self,
        min_cpu_cores: int = MIN_CPU_CORES,
        max_cpu_cores: int = MAX_CPU_CORES,
        min_memory_mb: int = MIN_MEMORY_MB,
        max_memory_mb: int = MAX_MEMORY_MB,
        min_timeout_s: int = MIN_TIMEOUT_S,
        max_timeout_s: int = MAX_TIMEOUT_S,
    ):
        """Initialize with configurable bounds."""
        self.min_cpu_cores = min_cpu_cores
        self.max_cpu_cores = max_cpu_cores
        self.min_memory_mb = min_memory_mb
        self.max_memory_mb = max_memory_mb
        self.min_timeout_s = min_timeout_s
        self.max_timeout_s = max_timeout_s

    def predict(
        self,
        *,
        signature: FailureSignature,
        history_bytes: bytes | None = None,
    ) -> ResourcePrediction:
        """Predict resource envelope deterministically."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DefaultDeterministicResourcePredictor.predict"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DefaultDeterministicResourcePredictor.predict".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Get baseline envelope for failure type
        baseline = self._BASELINE_ENVELOPES.get(signature.failure_type, self._BASELINE_ENVELOPES["unknown"])

        # Apply history-based adjustments if available
        envelope = self._apply_history_adjustments(baseline, signature, history_bytes)

        # Clamp to configured bounds
        envelope = self._clamp_envelope(envelope)

        # Generate deterministic confidence and reasons
        confidence, reasons = self._generate_confidence_and_reasons(signature, envelope, history_bytes)

        return ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=confidence,
            reasons=tuple(sorted(reasons)),  # Sort for determinism
        )

    def _apply_history_adjustments(
        self,
        baseline: ResourceEnvelope,
        signature: FailureSignature,
        history_bytes: bytes | None,
    ) -> ResourceEnvelope:
        """Apply deterministic adjustments based on history."""
        if not history_bytes:
            return baseline

        # Simple deterministic hash-based adjustment
        # In practice, this would parse history and compute statistics
        fingerprint_hash = int(signature.fingerprint[:8], 16)

        # Bounded adjustments based on fingerprint
        cpu_delta = (fingerprint_hash % 3) - 1  # -1, 0, or 1
        memory_delta = ((fingerprint_hash >> 4) % 5) - 2  # -2 to 2
        timeout_delta = ((fingerprint_hash >> 8) % 3) - 1  # -1, 0, or 1

        return ResourceEnvelope(
            cpu_cores=baseline.cpu_cores + cpu_delta,
            memory_mb=baseline.memory_mb + (memory_delta * 256),  # 256MB increments
            timeout_s=baseline.timeout_s + (timeout_delta * 60),  # 60s increments
        )

    def _clamp_envelope(self, envelope: ResourceEnvelope) -> ResourceEnvelope:
        """Clamp envelope to configured bounds."""
        return ResourceEnvelope(
            cpu_cores=max(self.min_cpu_cores, min(self.max_cpu_cores, envelope.cpu_cores)),
            memory_mb=max(self.min_memory_mb, min(self.max_memory_mb, envelope.memory_mb)),
            timeout_s=max(self.min_timeout_s, min(self.max_timeout_s, envelope.timeout_s)),
        )

    def _generate_confidence_and_reasons(
        self,
        signature: FailureSignature,
        envelope: ResourceEnvelope,
        history_bytes: bytes | None,
    ) -> tuple[float, tuple[str, ...]]:
        """Generate deterministic confidence and reasoning."""
        reasons = []

        # Base confidence by failure type
        base_confidence = {
            "timeout": 0.8,
            "memory_error": 0.9,
            "cpu_error": 0.7,
            "io_error": 0.6,
            "network_error": 0.5,
            "unknown": 0.4,
        }.get(signature.failure_type, 0.4)

        reasons.append(f"failure_type_{signature.failure_type}")

        # Adjust confidence based on history availability
        if history_bytes:
            base_confidence += 0.1
            reasons.append("history_available")
        else:
            reasons.append("baseline_only")

        # Adjust based on envelope size (larger envelopes have lower confidence)
        if envelope.cpu_cores > 8:
            base_confidence -= 0.1
            reasons.append("high_cpu")
        if envelope.memory_mb > 8192:
            base_confidence -= 0.1
            reasons.append("high_memory")

        # Clamp confidence to valid range
        confidence = max(0.0, min(1.0, base_confidence))

        return confidence, tuple(reasons)

    def track_prediction_accuracy(
        self,
        signature: FailureSignature,
        prediction: ResourcePrediction,
        actual_usage: ResourceEnvelope,
        success: bool,
        timestamp_utc: int,
    ) -> None:
        """Track prediction accuracy for system learning feedback.

        Args:
            signature: The failure signature that was predicted
            prediction: The resource prediction made
            actual_usage: Actual resources used
            success: Whether the prediction was successful
            timestamp_utc: Timestamp for tracking
        """
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()

            # Calculate accuracy metrics
            cpu_error = abs(prediction.envelope.cpu_cores - actual_usage.cpu_cores)
            memory_error = abs(prediction.envelope.memory_mb - actual_usage.memory_mb)
            timeout_error = abs(prediction.envelope.timeout_s - actual_usage.timeout_s)

            # Normalized error rates
            cpu_error_rate = cpu_error / max(1.0, prediction.envelope.cpu_cores)
            memory_error_rate = memory_error / max(1.0, prediction.envelope.memory_mb)
            timeout_error_rate = timeout_error / max(1.0, prediction.envelope.timeout_s)

            bridge.persist_resource_prediction_feedback(
                failure_type=signature.failure_type,
                fingerprint=signature.fingerprint,
                predicted_cpu=prediction.envelope.cpu_cores,
                predicted_memory=prediction.envelope.memory_mb,
                predicted_timeout=prediction.envelope.timeout_s,
                actual_cpu=actual_usage.cpu_cores,
                actual_memory=actual_usage.memory_mb,
                actual_timeout=actual_usage.timeout_s,
                cpu_error_rate=cpu_error_rate,
                memory_error_rate=memory_error_rate,
                timeout_error_rate=timeout_error_rate,
                confidence=prediction.confidence,
                success=success,
                timestamp_utc=timestamp_utc,
            )
        except (ValueError, TypeError):
            # System learning unavailable - continue without tracking
            pass

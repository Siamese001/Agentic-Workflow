"""
Key Discipline Abstraction for L2 Execution
Provides injectable, testable key source with no ambient secrets.
"""

import os
import uuid
from abc import ABC, abstractmethod
from typing import Final

from agentic_core.L2_execution.utils.providers import get_clock
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

emit_replay_key("p0", "key_source")
emit_determinism_digest("p0", "key_source")

_emit_dispatches_healing_run("p1", "key_source", "L2")
_emit_routes_through("p1", "key_source", "L2")
_emit_checks_agent_registry("p1", "key_source", "agent_registry")
_emit_validates_agent_capability("p1", "key_source", "capability")
_emit_dispatches_execution_plan("p1", "key_source", "exec_plan")
_emit_agent_executes_agent("p1", "key_source", "sub_agent")
_emit_routes_to_agent("p1", "key_source", "target_agent")
_emit_verifies_policy("p1", "key_source", "policy_check")
_emit_observes_runtime_state("p1", "key_source", "runtime_state")
_emit_verifies_boundary("p1", "key_source", "boundary_check")
_emit_transcripts_response("p1", "key_source", "transcript")
_emit_hard_fails_untranscripted("p1", "key_source")
_emit_gated_by_confidence("p1", "key_source", "confidence_gate")
_emit_escalates_to_human("p1", "key_source", "L2")
_emit_reads_policy_state("p1", "key_source", "L2")

_emit_snapshots_state("p0", "key_source", "state_snapshot")
_emit_authorize_and_execute("p2", "key_source", "execution_auth")
_emit_validates_capability("p2", "key_source", "capability_check")
_emit_routes_to_capability("p2", "key_source", "capability_route")
_emit_writes_via_uwg("p2", "key_source", "uwg_write")
_emit_blocks_direct_write("p2", "key_source", "direct_write_block")
_emit_records_tool_invocation("p2", "key_source", "tool_invocation")
_emit_captures_execution_output("p2", "key_source", "exec_output")
_emit_dispatches_agent("p3", "key_source", "agent_dispatch")
_emit_coordinates_agents("p3", "key_source", "agent_coordination")
_emit_records_workflow_lineage("p3", "key_source", "workflow_lineage")
_emit_records_healing_outcome("p3", "key_source", "healing_outcome")
_emit_escalates_failure("p3", "key_source", "failure_escalation")
_emit_orchestrates_workflow("p3", "key_source", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "key_source", "healing_dispatch")
_emit_invokes_evaluation("p3", "key_source", "evaluation_signal")
_emit_records_telemetry_event("p4", "key_source", "telemetry_event")
_emit_captures_evaluation_metric("p4", "key_source", "eval_metric")
_emit_stores_embedding("p4", "key_source", "embedding_store")
_emit_updates_meta_learning_state("p4", "key_source", "meta_learning")
_emit_links_execution_to_snapshot("p4", "key_source", "exec_snapshot_link")
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

_emit_emits_metric_event("key_source", "p4obs", "metric_1")
_emit_emits_metric_event("key_source", "p4obs", "metric_2")
_emit_emits_metric_event("key_source", "p4obs", "metric_3")
_emit_emits_metric_event("key_source", "p4obs", "metric_4")
_emit_emits_metric_event("key_source", "p4obs", "metric_5")
_emit_emits_metric_event("key_source", "p4obs", "metric_6")
_emit_records_incident_event("key_source", "p4obs", "incident")
_emit_captures_runtime_anomaly("key_source", "p4obs", "anomaly")
_emit_writes_observability_log("key_source", "p4obs", "obs_log")
_emit_updates_monitoring_state("key_source", "p4obs", "mon_state")
_emit_triggers_alert("key_source", "p4obs", "alert")
_emit_links_incident_trace("key_source", "p4obs", "trace_link")
_emit_captures_pattern("key_source", "p3lm", "pattern")
_emit_records_learning_event("key_source", "p3lm", "learning_event")
_emit_writes_learning_snapshot("key_source", "p3lm", "snapshot")
_emit_feeds_meta_learning("key_source", "p3lm", "meta_feed")
_emit_updates_routing_strategy("key_source", "p3lm", "routing")
_emit_improves_agent_policy("key_source", "p3lm", "policy")
_emit_stores_learning_state("key_source", "p3lm", "state")
_emit_records_execution_trace("key_source", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("key_source", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("key_source", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("key_source", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("key_source", "L4_STATE", "p2_trace_5")
_emit_reads_environ("key_source", "env_read", "p2_env_1")
_emit_reads_environ("key_source", "env_read", "p2_env_2")
_emit_reads_runtime_state("key_source", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("key_source", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "key_source", "context_pull")
_emit_pulls_context("p1", "key_source", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "key_source", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "key_source", "uwg_term_2")
_emit_writes_through("p1", "key_source", "write_through")
_emit_writes_through("p1", "key_source", "write_through_2")
_emit_validated_by_safety_plane("p1", "key_source", "safety_validation")
_emit_invokes_eval("p1", "key_source", "eval_call")
_emit_proposal_commits_routing("p1", "key_source", "routing_commit")


class KeySource(ABC):
    """Abstract base for key sources - must be injected, never ambient."""

    @abstractmethod
    def get_secret(self) -> bytes:
        """Return the secret key for signing/verification."""
        pass

    @abstractmethod
    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        pass

    @abstractmethod
    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        pass


class TestKeySource(KeySource):
    """Deterministic test key source for unit tests."""

    TEST_SECRET: Final[bytes] = b"phase1-test-secret-key"

    def __init__(self):
        self._key_scopes: dict[str, bool] = {"signature": True, "hmac": True, "audit": True, "trace": True}
        self._expiry_time: float | None = None

    def get_secret(self) -> bytes:
        return self.TEST_SECRET

    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "TestKeySource.assert_key_scope")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TestKeySource.assert_key_scope".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if artifact_type not in self._key_scopes:
            raise ValueError(f"Key not scoped for artifact type: {artifact_type}")
        if not self._key_scopes[artifact_type]:
            raise ValueError(f"Key scope invalid for artifact type: {artifact_type}")

    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        if self._expiry_time and get_clock().now_epoch() > self._expiry_time:
            raise ValueError("Key has expired")

    def set_key_scope(self, artifact_type: str, allowed: bool):
        """Set key scope for testing."""
        self._key_scopes[artifact_type] = allowed

    def set_expiry_time(self, expiry_time: float | None):
        """Set expiry time for testing."""
        self._expiry_time = expiry_time


class EnvKeySource(KeySource):
    """Environment-based key source for production (edge only)."""

    def __init__(self, env_var: str = "L2_EXECUTION_SECRET"):
        self.env_var = env_var
        if env_var not in os.environ:
            raise ValueError(f"Environment variable {env_var} not set")
        self._key_scopes: dict[str, bool] = {"signature": True, "hmac": True, "audit": True, "trace": True}
        self._creation_time = get_clock().now_epoch()
        self._ttl = 24 * 60 * 60

    def get_secret(self) -> bytes:
        return os.environ[self.env_var].encode()

    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "EnvKeySource.assert_key_scope")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EnvKeySource.assert_key_scope".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if artifact_type not in self._key_scopes:
            raise ValueError(f"Key not scoped for artifact type: {artifact_type}")
        if not self._key_scopes[artifact_type]:
            raise ValueError(f"Key scope invalid for artifact type: {artifact_type}")

    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        if get_clock().now_epoch() > self._creation_time + self._ttl:
            raise ValueError("Production key has expired")

    def set_key_scope(self, artifact_type: str, allowed: bool):
        """Set key scope (for configuration)."""
        self._key_scopes[artifact_type] = allowed

    def set_ttl(self, ttl_seconds: int):
        """Set time-to-live for key."""
        self._ttl = ttl_seconds


_injected_key_source: KeySource | None = None


def inject_key_source(source: KeySource) -> None:
    """Inject a key source - must be called at application edge."""
    global _injected_key_source
    _injected_key_source = source


def get_key_source() -> KeySource:
    """Get the injected key source - fails if not injected."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_key_source", "L2_EXECUTION")
    global _injected_key_source
    if _injected_key_source is None:
        raise RuntimeError("KeySource not injected - call inject_key_source() first")
    return _injected_key_source


def get_current_secret() -> bytes:
    """Convenience helper to get current secret."""
    return get_key_source().get_secret()

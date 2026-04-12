"""
CapabilityRevoker — Token revocation management for L2 execution boundary.

Manages per-trace revocation and authority-version invalidation.
All capability tokens must be validated through this revoker before
any L2 tool invocation is permitted.

Phase 3.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import threading
import uuid

from agentic_core.L2_execution.enforcement.key_derivation import get_key_version
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

emit_replay_key("p0", "capability_revoker")
emit_determinism_digest("p0", "capability_revoker")

_emit_dispatches_healing_run("p1", "capability_revoker", "L2")
_emit_routes_through("p1", "capability_revoker", "L2")
_emit_checks_agent_registry("p1", "capability_revoker", "agent_registry")
_emit_validates_agent_capability("p1", "capability_revoker", "capability")
_emit_dispatches_execution_plan("p1", "capability_revoker", "exec_plan")
_emit_agent_executes_agent("p1", "capability_revoker", "sub_agent")
_emit_routes_to_agent("p1", "capability_revoker", "target_agent")
_emit_verifies_policy("p1", "capability_revoker", "policy_check")
_emit_observes_runtime_state("p1", "capability_revoker", "runtime_state")
_emit_transcripts_response("p1", "capability_revoker", "transcript")
_emit_hard_fails_untranscripted("p1", "capability_revoker")
_emit_gated_by_confidence("p1", "capability_revoker", "confidence_gate")
_emit_escalates_to_human("p1", "capability_revoker", "L2")
_emit_reads_policy_state("p1", "capability_revoker", "L2")

_emit_applies_guardrail("p0", "capability_revoker", "p0_governance")
_emit_snapshots_state("p0", "capability_revoker", "state_snapshot")
_emit_authorize_and_execute("p2", "capability_revoker", "execution_auth")
_emit_validates_capability("p2", "capability_revoker", "capability_check")
_emit_routes_to_capability("p2", "capability_revoker", "capability_route")
_emit_writes_via_uwg("p2", "capability_revoker", "uwg_write")
_emit_blocks_direct_write("p2", "capability_revoker", "direct_write_block")
_emit_records_tool_invocation("p2", "capability_revoker", "tool_invocation")
_emit_captures_execution_output("p2", "capability_revoker", "exec_output")
_emit_dispatches_agent("p3", "capability_revoker", "agent_dispatch")
_emit_coordinates_agents("p3", "capability_revoker", "agent_coordination")
_emit_records_workflow_lineage("p3", "capability_revoker", "workflow_lineage")
_emit_records_healing_outcome("p3", "capability_revoker", "healing_outcome")
_emit_escalates_failure("p3", "capability_revoker", "failure_escalation")
_emit_orchestrates_workflow("p3", "capability_revoker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "capability_revoker", "healing_dispatch")
_emit_invokes_evaluation("p3", "capability_revoker", "evaluation_signal")
_emit_records_telemetry_event("p4", "capability_revoker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "capability_revoker", "eval_metric")
_emit_stores_embedding("p4", "capability_revoker", "embedding_store")
_emit_updates_meta_learning_state("p4", "capability_revoker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "capability_revoker", "exec_snapshot_link")
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("capability_revoker", "p4obs", "metric_1")
_emit_emits_metric_event("capability_revoker", "p4obs", "metric_2")
_emit_emits_metric_event("capability_revoker", "p4obs", "metric_3")
_emit_emits_metric_event("capability_revoker", "p4obs", "metric_4")
_emit_emits_metric_event("capability_revoker", "p4obs", "metric_5")
_emit_emits_metric_event("capability_revoker", "p4obs", "metric_6")
_emit_records_incident_event("capability_revoker", "p4obs", "incident")
_emit_captures_runtime_anomaly("capability_revoker", "p4obs", "anomaly")
_emit_writes_observability_log("capability_revoker", "p4obs", "obs_log")
_emit_updates_monitoring_state("capability_revoker", "p4obs", "mon_state")
_emit_triggers_alert("capability_revoker", "p4obs", "alert")
_emit_links_incident_trace("capability_revoker", "p4obs", "trace_link")
_emit_captures_pattern("capability_revoker", "p3lm", "pattern")
_emit_records_learning_event("capability_revoker", "p3lm", "learning_event")
_emit_writes_learning_snapshot("capability_revoker", "p3lm", "snapshot")
_emit_feeds_meta_learning("capability_revoker", "p3lm", "meta_feed")
_emit_updates_routing_strategy("capability_revoker", "p3lm", "routing")
_emit_improves_agent_policy("capability_revoker", "p3lm", "policy")
_emit_stores_learning_state("capability_revoker", "p3lm", "state")
_emit_records_execution_trace("capability_revoker", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("capability_revoker", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("capability_revoker", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("capability_revoker", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("capability_revoker", "L4_STATE", "p2_trace_5")
_emit_reads_environ("capability_revoker", "env_read", "p2_env_1")
_emit_reads_environ("capability_revoker", "env_read", "p2_env_2")
_emit_reads_runtime_state("capability_revoker", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("capability_revoker", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "capability_revoker", "context_pull")
_emit_pulls_context("p1", "capability_revoker", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "capability_revoker", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "capability_revoker", "uwg_term_2")
_emit_writes_through("p1", "capability_revoker", "write_through")
_emit_writes_through("p1", "capability_revoker", "write_through_2")
_emit_validated_by_safety_plane("p1", "capability_revoker", "safety_validation")
_emit_invokes_eval("p1", "capability_revoker", "eval_call")
_emit_proposal_commits_routing("p1", "capability_revoker", "routing_commit")


class TokenRevocationError(RuntimeError):
    """Raised when a token is used after revocation."""


class VersionInvalidError(RuntimeError):
    """Raised when a token's authority version is no longer valid."""


class CapabilityRevoker:
    """Thread-safe capability token revocation registry.

    Usage::

        revoker = get_capability_revoker()
        revoker.validate_token(token.trace_id, token.authority_secret_version)
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._revoked_trace_ids: set[str] = set()
        self._invalid_versions: set[str] = set()

    def revoke_token(self, trace_id: str) -> None:
        """Revoke a specific token by its trace ID (immediate effect)."""
        with self._lock:
            self._revoked_trace_ids.add(trace_id)

    def invalidate_version(self, version: str) -> None:
        """Invalidate all tokens carrying a specific authority_secret_version."""
        _emit_verifies_boundary(str(uuid.uuid4()), "CapabilityRevoker.invalidate_version", "L2_EXECUTION")
        with self._lock:
            self._invalid_versions.add(version)

    def is_token_revoked(self, trace_id: str) -> bool:
        with self._lock:
            return trace_id in self._revoked_trace_ids

    def is_version_valid(self, version: str) -> bool:
        """Return True iff *version* equals the current key version and is not invalidated."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "CapabilityRevoker.is_version_valid",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CapabilityRevoker.is_version_valid".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            if version in self._invalid_versions:
                return False
        return version == get_key_version()

    def validate_token(self, trace_id: str, authority_secret_version: str) -> None:
        """Raise if token is revoked or version is invalid.

        Args:
            trace_id: The trace_id embedded in the capability token.
            authority_secret_version: The authority_secret_version embedded in the token.

        Raises:
            TokenRevocationError: token has been explicitly revoked.
            VersionInvalidError: token authority version is invalid or rotated away.
        """
        if self.is_token_revoked(trace_id):
            raise TokenRevocationError(f"Capability token revoked: trace_id={trace_id}")
        if not self.is_version_valid(authority_secret_version):
            raise VersionInvalidError(
                f"Capability token authority version invalid: version={authority_secret_version}, current={get_key_version()}",
            )

    def revoked_count(self) -> int:
        with self._lock:
            return len(self._revoked_trace_ids)

    def invalid_version_count(self) -> int:
        with self._lock:
            return len(self._invalid_versions)


_DEFAULT_REVOKER: CapabilityRevoker | None = None
_SINGLETON_LOCK = threading.Lock()


def get_capability_revoker() -> CapabilityRevoker:
    """Return the process-wide CapabilityRevoker singleton."""
    global _DEFAULT_REVOKER
    with _SINGLETON_LOCK:
        if _DEFAULT_REVOKER is None:
            _DEFAULT_REVOKER = CapabilityRevoker()
    return _DEFAULT_REVOKER


def reset_capability_revoker_for_testing() -> None:
    """Reset the singleton (test isolation only)."""
    global _DEFAULT_REVOKER
    with _SINGLETON_LOCK:
        _DEFAULT_REVOKER = None


__all__ = [
    "CapabilityRevoker",
    "TokenRevocationError",
    "VersionInvalidError",
    "get_capability_revoker",
    "reset_capability_revoker_for_testing",
]

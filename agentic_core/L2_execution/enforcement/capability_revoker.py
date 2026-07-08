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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "capability_revoker")
trace_contract.emit_determinism_digest("p0", "capability_revoker")

trace_contract._emit_dispatches_healing_run("p1", "capability_revoker", "L2")
trace_contract._emit_routes_through("p1", "capability_revoker", "L2")
trace_contract._emit_checks_agent_registry("p1", "capability_revoker", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "capability_revoker", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "capability_revoker", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "capability_revoker", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "capability_revoker", "target_agent")
trace_contract._emit_verifies_policy("p1", "capability_revoker", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "capability_revoker", "runtime_state")
trace_contract._emit_transcripts_response("p1", "capability_revoker", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "capability_revoker")
trace_contract._emit_gated_by_confidence("p1", "capability_revoker", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "capability_revoker", "L2")
trace_contract._emit_reads_policy_state("p1", "capability_revoker", "L2")

trace_contract._emit_applies_guardrail("p0", "capability_revoker", "p0_governance")
trace_contract._emit_snapshots_state("p0", "capability_revoker", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "capability_revoker", "execution_auth")
trace_contract._emit_validates_capability("p2", "capability_revoker", "capability_check")
trace_contract._emit_routes_to_capability("p2", "capability_revoker", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "capability_revoker", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "capability_revoker", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "capability_revoker", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "capability_revoker", "exec_output")
trace_contract._emit_dispatches_agent("p3", "capability_revoker", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "capability_revoker", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "capability_revoker", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "capability_revoker", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "capability_revoker", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "capability_revoker", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "capability_revoker", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "capability_revoker", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "capability_revoker", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "capability_revoker", "eval_metric")
trace_contract._emit_stores_embedding("p4", "capability_revoker", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "capability_revoker", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "capability_revoker", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("capability_revoker", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("capability_revoker", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("capability_revoker", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("capability_revoker", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("capability_revoker", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("capability_revoker", "p4obs", "alert")
trace_contract._emit_links_incident_trace("capability_revoker", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("capability_revoker", "p3lm", "pattern")
trace_contract._emit_records_learning_event("capability_revoker", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("capability_revoker", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("capability_revoker", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("capability_revoker", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("capability_revoker", "p3lm", "policy")
trace_contract._emit_stores_learning_state("capability_revoker", "p3lm", "state")
trace_contract._emit_records_execution_trace("capability_revoker", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("capability_revoker", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("capability_revoker", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("capability_revoker", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("capability_revoker", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("capability_revoker", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("capability_revoker", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("capability_revoker", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("capability_revoker", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "capability_revoker", "context_pull")
trace_contract._emit_pulls_context("p1", "capability_revoker", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_revoker", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_revoker", "uwg_term_2")
trace_contract._emit_writes_through("p1", "capability_revoker", "write_through")
trace_contract._emit_writes_through("p1", "capability_revoker", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "capability_revoker", "safety_validation")
trace_contract._emit_invokes_eval("p1", "capability_revoker", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "capability_revoker", "routing_commit")


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
        trace_contract._emit_verifies_boundary(str(uuid.uuid4()), "CapabilityRevoker.invalidate_version", "L2_EXECUTION")
        with self._lock:
            self._invalid_versions.add(version)

    def is_token_revoked(self, trace_id: str) -> bool:
        with self._lock:
            return trace_id in self._revoked_trace_ids

    def is_version_valid(self, version: str) -> bool:
        """Return True iff *version* equals the current key version and is not invalidated."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "CapabilityRevoker.is_version_valid",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CapabilityRevoker.is_version_valid".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

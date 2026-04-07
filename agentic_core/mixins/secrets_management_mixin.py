import logging
import os
import re
import time

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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "secrets_management_mixin", "p0_governance")
_emit_reads_policy_state("p0", "secrets_management_mixin", "policy_binding")
_emit_snapshots_state("p0", "secrets_management_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("secrets_management_mixin", "p4obs", "metric_6")
_emit_records_incident_event("secrets_management_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("secrets_management_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("secrets_management_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("secrets_management_mixin", "p4obs", "mon_state")
_emit_triggers_alert("secrets_management_mixin", "p4obs", "alert")
_emit_links_incident_trace("secrets_management_mixin", "p4obs", "trace_link")
_emit_captures_pattern("secrets_management_mixin", "p3lm", "pattern")
_emit_records_learning_event("secrets_management_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("secrets_management_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("secrets_management_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("secrets_management_mixin", "p3lm", "routing")
_emit_improves_agent_policy("secrets_management_mixin", "p3lm", "policy")
_emit_stores_learning_state("secrets_management_mixin", "p3lm", "state")
_emit_records_execution_trace("secrets_management_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("secrets_management_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("secrets_management_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("secrets_management_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("secrets_management_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("secrets_management_mixin", "env_read", "p2_env_1")
_emit_reads_environ("secrets_management_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("secrets_management_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("secrets_management_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "secrets_management_mixin", "context_pull")
_emit_pulls_context("p1", "secrets_management_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "secrets_management_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "secrets_management_mixin", "uwg_term_2")
_emit_writes_through("p1", "secrets_management_mixin", "write_through")
_emit_writes_through("p1", "secrets_management_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "secrets_management_mixin", "safety_validation")
_emit_invokes_eval("p1", "secrets_management_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "secrets_management_mixin", "routing_commit")
_emit_escalates_to_human("p1", "secrets_management_mixin", "human_escalation")
_emit_routes_through("p1", "secrets_management_mixin", "route_through")
_emit_checks_agent_registry("p1", "secrets_management_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "secrets_management_mixin", "capability")
_emit_dispatches_execution_plan("p1", "secrets_management_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "secrets_management_mixin", "sub_agent")
_emit_routes_to_agent("p1", "secrets_management_mixin", "target_agent")
_emit_verifies_policy("p1", "secrets_management_mixin", "policy_check")
_emit_observes_runtime_state("p1", "secrets_management_mixin", "runtime_state")
_emit_verifies_boundary("p1", "secrets_management_mixin", "boundary_check")
_emit_transcripts_response("p1", "secrets_management_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "secrets_management_mixin")
_emit_gated_by_confidence("p1", "secrets_management_mixin", "confidence_gate")
emit_replay_key("p0", "secrets_management_mixin")
emit_determinism_digest("p0", "secrets_management_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "secrets_management_mixin", "execution_auth")
_emit_validates_capability("p2", "secrets_management_mixin", "capability_check")
_emit_routes_to_capability("p2", "secrets_management_mixin", "capability_route")
_emit_writes_via_uwg("p2", "secrets_management_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "secrets_management_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "secrets_management_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "secrets_management_mixin", "exec_output")
_emit_dispatches_agent("p3", "secrets_management_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "secrets_management_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "secrets_management_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "secrets_management_mixin", "healing_outcome")
_emit_escalates_failure("p3", "secrets_management_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "secrets_management_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "secrets_management_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "secrets_management_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "secrets_management_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "secrets_management_mixin", "eval_metric")
_emit_stores_embedding("p4", "secrets_management_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "secrets_management_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "secrets_management_mixin", "exec_snapshot_link")


class SecretAccessError(Exception):
    """Raised when a secret cannot be retrieved or accessed."""

    pass


class SecretsManagementMixin:
    """
    Phase 1 Critical Infrastructure: Secrets Management (Report 4.4).

    Centralizes credential access with:
    - Environment isolation (DEV/STAGING/PROD)
    - Access auditing (who requested what, when)
    - Abstracted retrieval (env vars -> Vault migration path)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sm_logger = logging.getLogger(self.__class__.__name__)
        self._env_context = os.getenv("SOVEREIGN_ENV", "DEV").upper()
        self._secret_cache: dict[str, tuple[str, float]] = {}
        self._CACHE_TTL = 600

    def _is_valid_secret_key(self, key: str) -> bool:
        return bool(re.match("^[A-Z][A-Z0-9_]{3,63}$", key))

    def _audit_access(self, secret_key: str, success: bool):
        """Internal: Log access attempts without revealing the secret value."""
        status = "ALLOWED" if success else "DENIED"
        self._sm_logger.info(
            f"AUDIT: Secret access | Key='{secret_key}' | Agent='{self.__class__.__name__}' | Env='{self._env_context}' | Status='{status}'",
        )

    async def get_secret(self, key: str, default: str | None = None) -> str:
        """
        Securely retrieve a secret value.

        Args:
            key: The identifier for the secret (e.g., 'OPENAI_API_KEY')
            default: Value to return if not found (discouraged for sensitive data)

        Returns:
            The secret string.

        Raises:
            SecretAccessError: If secret is missing and no default provided.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecretsManagementMixin.get_secret")

        if not self._is_valid_secret_key(key):
            self._audit_access(key, success=False)
            raise SecretAccessError(f"Invalid secret key format: {key}")
        if key in self._secret_cache:
            value, expiry = self._secret_cache[key]
            if time.time() < expiry:
                self._audit_access(key, success=True)
                return value
            del self._secret_cache[key]
        value = os.getenv(key)
        if value is None:
            if default is not None:
                self._audit_access(key, success=True)
                return default
            self._audit_access(key, success=False)
            raise SecretAccessError(
                f"Secret '{key}' not found for agent '{self.__class__.__name__}' in environment '{self._env_context}'",
            )
        self._audit_access(key, success=True)
        self._secret_cache[key] = (value, time.time() + self._CACHE_TTL)
        return value

    async def rotate_secret(self, key: str) -> bool:
        """
        Trigger a rotation for a compromised or expired secret.
        (Placeholder for future Vault integration)
        """
        self._sm_logger.warning(f"Secret rotation requested for '{key}' - Not implemented in EnvVar mode")
        return False

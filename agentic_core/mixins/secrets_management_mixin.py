import logging
import os
import re
import time

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "secrets_management_mixin", "p0_governance")
_emit_reads_policy_state("p0", "secrets_management_mixin", "policy_binding")
_emit_snapshots_state("p0", "secrets_management_mixin", "state_snapshot")
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
            f"AUDIT: Secret access | Key='{secret_key}' | Agent='{self.__class__.__name__}' | Env='{self._env_context}' | Status='{status}'"
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
                f"Secret '{key}' not found for agent '{self.__class__.__name__}' in environment '{self._env_context}'"
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

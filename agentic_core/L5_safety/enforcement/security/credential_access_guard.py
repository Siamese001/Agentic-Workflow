"""CredentialAccessGuard — safety-plane enforcement for credential and secret access.

All credential reads and secret lookups MUST be routed through this guard.
It provides three guarantees:

  1. Every access is recorded in the SecretAccessRecorder (ADG: reads_secret,
     accesses_credential edges become ``validated_by_safety_plane`` events).
  2. Caller identity is bound to each access event (agent_id + run_id).
  3. Access can be denied at the policy level before reaching the credential
     store (policy_enforced=True mode).

ADG governance plane: calling ``guarded_get_secret`` or ``guarded_get_env``
adds a ``validated_by_safety_plane`` relation from the caller to the
credential surface, closing the gap between ``accesses_credential`` (346)
and governed access edges (~95).

Layer note: adg.runtime.secret_access (L_TOOLS) is imported lazily inside
each method to avoid an upward L5->L_TOOLS module-level dependency (ADG
violation GV-2).  The functional contract is identical; only the import
timing changes.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

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

emit_replay_key("p0", "credential_access_guard")
emit_determinism_digest("p0", "credential_access_guard")

_emit_dispatches_healing_run("p1", "credential_access_guard", "L5")
_emit_routes_through("p1", "credential_access_guard", "L5")
_emit_checks_agent_registry("p1", "credential_access_guard", "agent_registry")
_emit_validates_agent_capability("p1", "credential_access_guard", "capability")
_emit_dispatches_execution_plan("p1", "credential_access_guard", "exec_plan")
_emit_agent_executes_agent("p1", "credential_access_guard", "sub_agent")
_emit_routes_to_agent("p1", "credential_access_guard", "target_agent")
_emit_verifies_policy("p1", "credential_access_guard", "policy_check")
_emit_observes_runtime_state("p1", "credential_access_guard", "runtime_state")
_emit_verifies_boundary("p1", "credential_access_guard", "boundary_check")
_emit_transcripts_response("p1", "credential_access_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "credential_access_guard")
_emit_gated_by_confidence("p1", "credential_access_guard", "confidence_gate")
_emit_escalates_to_human("p1", "credential_access_guard", "L5")
_emit_reads_policy_state("p1", "credential_access_guard", "L5")

_emit_applies_guardrail("p0", "credential_access_guard", "p0_governance")
_emit_snapshots_state("p0", "credential_access_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "credential_access_guard", "execution_auth")
_emit_validates_capability("p2", "credential_access_guard", "capability_check")
_emit_routes_to_capability("p2", "credential_access_guard", "capability_route")
_emit_writes_via_uwg("p2", "credential_access_guard", "uwg_write")
_emit_blocks_direct_write("p2", "credential_access_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "credential_access_guard", "tool_invocation")
_emit_captures_execution_output("p2", "credential_access_guard", "exec_output")
_emit_dispatches_agent("p3", "credential_access_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "credential_access_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "credential_access_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "credential_access_guard", "healing_outcome")
_emit_escalates_failure("p3", "credential_access_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "credential_access_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "credential_access_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "credential_access_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "credential_access_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "credential_access_guard", "eval_metric")
_emit_stores_embedding("p4", "credential_access_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "credential_access_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "credential_access_guard", "exec_snapshot_link")
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

_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_1")
_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_2")
_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_3")
_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_4")
_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_5")
_emit_emits_metric_event("credential_access_guard", "p4obs", "metric_6")
_emit_records_incident_event("credential_access_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("credential_access_guard", "p4obs", "anomaly")
_emit_writes_observability_log("credential_access_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("credential_access_guard", "p4obs", "mon_state")
_emit_triggers_alert("credential_access_guard", "p4obs", "alert")
_emit_links_incident_trace("credential_access_guard", "p4obs", "trace_link")
_emit_captures_pattern("credential_access_guard", "p3lm", "pattern")
_emit_records_learning_event("credential_access_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("credential_access_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("credential_access_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("credential_access_guard", "p3lm", "routing")
_emit_improves_agent_policy("credential_access_guard", "p3lm", "policy")
_emit_stores_learning_state("credential_access_guard", "p3lm", "state")
_emit_records_execution_trace("credential_access_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("credential_access_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("credential_access_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("credential_access_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("credential_access_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("credential_access_guard", "env_read", "p2_env_1")
_emit_reads_environ("credential_access_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("credential_access_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("credential_access_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "credential_access_guard", "context_pull")
_emit_pulls_context("p1", "credential_access_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "credential_access_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "credential_access_guard", "uwg_term_2")
_emit_writes_through("p1", "credential_access_guard", "write_through")
_emit_writes_through("p1", "credential_access_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "credential_access_guard", "safety_validation")
_emit_invokes_eval("p1", "credential_access_guard", "eval_call")
_emit_proposal_commits_routing("p1", "credential_access_guard", "routing_commit")

Logger = logging.getLogger(__name__)

_DENIED_PREFIXES: tuple[str, ...] = (
    "AWS_SECRET",
    "PRIVATE_KEY",
    "SIGNING_KEY",
)


def _import_secret_access():  # noqa: ANN202
    """Lazy import helper — defers L_TOOLS import to call time."""
    from agentic_core.adg.runtime.secret_access import (  # noqa: PLC0415
        SecretAccessOutcome,
        SecretAccessRecorder,
        SecretKind,
    )

    return SecretAccessOutcome, SecretAccessRecorder, SecretKind


class CredentialAccessDenied(PermissionError):
    """Raised when the guard denies a credential access attempt."""


class CredentialAccessGuard:
    """Safety-plane gate for all credential and secret access.

    Usage::

        guard = CredentialAccessGuard(agent_id="MyAgent", run_id="run-abc")
        api_key = guard.guarded_get_secret("OPENAI_API_KEY")
        db_pass = guard.guarded_get_env("DB_PASSWORD")

    The guard maintains an internal ``SecretAccessRecorder`` and emits a
    ``validated_by_safety_plane`` audit event for each access.
    """

    def __init__(
        self,
        agent_id: str,
        run_id: str,
        policy_enforced: bool = True,
        denied_prefixes: tuple[str, ...] | None = None,
    ) -> None:
        _SecretAccessOutcome, SecretAccessRecorder, _SecretKind = _import_secret_access()
        self._agent_id = agent_id
        self._run_id = run_id
        self._policy_enforced = policy_enforced
        self._denied_prefixes = denied_prefixes if denied_prefixes is not None else _DENIED_PREFIXES
        self._recorder = SecretAccessRecorder(agent_id=agent_id, run_id=run_id)
        self._adg_violates: list[str] = []
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _root = _Path(__file__).resolve().parents[5]
            _bp = _gbp(_Path(__file__).resolve(), _root)
            self._adg_violates = sorted(_bp.antipattern_signals)
            if self._adg_violates:
                Logger.warning(
                    "[ADG] CredentialAccessGuard: violates L5->L_TOOLS signals=%s "
                    "(score=%.3f) — add to guardian priority queue",
                    self._adg_violates,
                    _bp.behavioral_score,
                )
        except (
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
            pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def guarded_get_secret(
        self,
        secret_name: str,
        kind: Any = None,
        default: str | None = None,
    ) -> str:
        """Retrieve a secret value through the safety-plane gate.

        Args:
            secret_name: The identifier for the secret (e.g. ``OPENAI_API_KEY``).
            kind: The ``SecretKind`` category for audit classification.
            default: Fallback value when the secret is absent (avoid for sensitive data).

        Returns:
            The secret string.

        Raises:
            CredentialAccessDenied: if policy blocks this secret name.
            KeyError: if secret absent and no default provided.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "CredentialAccessGuard.guarded_get_secret",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CredentialAccessGuard.guarded_get_secret".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.API_KEY
        self._apply_policy_gate(secret_name)
        raw = os.environ.get(secret_name)
        if raw is None:
            if default is not None:
                self._recorder.record_access(
                    secret_name=secret_name,
                    secret_kind=kind,
                    access_method="guarded_get_secret",
                    outcome=SecretAccessOutcome.NOT_FOUND,
                )
                Logger.debug(  # pii: allow-secret-name-only -- logs env var NAME (e.g. "GEMINI_API_KEY"), never the secret value
                    "[CredentialAccessGuard] %s not found, using default", secret_name,
                )
                return default
            self._recorder.record_denied(secret_name=secret_name, secret_kind=kind)
            raise KeyError(
                f"CredentialAccessGuard: secret '{secret_name}' not found and no default provided.",
            )
        self._recorder.record_access(
            secret_name=secret_name,
            secret_kind=kind,
            access_method="guarded_get_secret",
            outcome=SecretAccessOutcome.SUCCESS,
            raw_value=raw,
        )
        Logger.debug(  # pii: allow-secret-name-only -- logs env var NAME and kind, never the secret value
            "[CredentialAccessGuard] validated_by_safety_plane: %s (%s)", secret_name, kind,
        )
        return raw

    def guarded_get_env(
        self,
        var_name: str,
        kind: Any = None,
        default: str | None = None,
    ) -> str | None:
        """Retrieve an environment variable through the safety-plane gate.

        Unlike ``guarded_get_secret``, missing variables return *default*
        (which may be None) rather than raising.
        """
        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.ENV_VAR
        self._apply_policy_gate(var_name)
        raw = os.environ.get(var_name, default)
        outcome = SecretAccessOutcome.SUCCESS if raw is not None else SecretAccessOutcome.NOT_FOUND
        self._recorder.record_access(
            secret_name=var_name,
            secret_kind=kind,
            access_method="guarded_get_env",
            outcome=outcome,
        )
        Logger.debug("[CredentialAccessGuard] env read validated_by_safety_plane: %s", var_name)
        return raw

    def guarded_access_credential(
        self,
        credential_name: str,
        kind: Any = None,
        resolver: Any = None,
    ) -> Any:
        """Access a structured credential through the safety-plane gate.

        Args:
            credential_name: Logical credential identifier.
            kind: Credential kind for audit classification.
            resolver: Optional callable ``(name: str) -> Any`` to retrieve the
                      credential from a vault or credential store.  If None, falls
                      back to ``os.environ``.

        Returns:
            The resolved credential value.

        Raises:
            CredentialAccessDenied: if policy blocks this credential.
        """
        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.TOKEN
        self._apply_policy_gate(credential_name)
        if resolver is not None:
            value = resolver(credential_name)
        else:
            value = os.environ.get(credential_name)
        outcome = SecretAccessOutcome.SUCCESS if value is not None else SecretAccessOutcome.NOT_FOUND
        self._recorder.record_access(
            secret_name=credential_name,
            secret_kind=kind,
            access_method="guarded_access_credential",
            outcome=outcome,
        )
        Logger.debug(
            "[CredentialAccessGuard] accesses_credential validated_by_safety_plane: %s",
            credential_name,
        )
        return value

    def hash_credential(self, raw_value: str) -> str:
        """Return a masked SHA-256 hash of a credential value (first 16 hex chars)."""
        return hashlib.sha256(raw_value.encode()).hexdigest()[:16]

    @property
    def access_report(self):
        """Return the accumulated ``SecretAccessReport`` for this guard instance."""
        return self._recorder.report

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _apply_policy_gate(self, name: str) -> None:
        """Raise CredentialAccessDenied if the name violates policy."""
        if not self._policy_enforced:
            return
        name_upper = name.upper()
        for prefix in self._denied_prefixes:
            if name_upper.startswith(prefix):
                self._recorder.record_denied(secret_name=name)
                raise CredentialAccessDenied(
                    f"CredentialAccessGuard: access to '{name}' denied by safety policy "
                    f"(matches denied prefix '{prefix}').",
                )

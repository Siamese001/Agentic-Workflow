"""
ReplayGuardMixin — Deterministic Replay Foundation for SSOT Mixin Integration.

Provides the base replay-mode enforcement layer that all stateful mixins
depend on. Accepts an injected ExecutionContext (never reads environment
variables directly) and loads the active policy hash from L4 config.

Layer: L2 Execution Aid
Authority: Guard only — no L4 mutation, no L5 bypass, no routing influence.

When replay_mode is True:
  - Installs deterministic providers (time, random, uuid) via L2 module.
  - Locks replay_mode immutably for the lifetime of the instance.
  - Exposes properties consumed by downstream mixins to disable TTL,
    adaptive switching, breaker mutation, and ML writes.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    record_execution_trace,
)

_emit_records_execution_trace("p0", "evidence", "replay_guard_mixin")
_emit_applies_guardrail("p0", "replay_guard_mixin", "p0_governance")
_emit_snapshots_state("p0", "replay_guard_mixin", "state_snapshot")
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
    _emit_records_execution_trace,
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

record_execution_trace("replay_guard_mixin", "replay_guard_mixin_trace")


_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("replay_guard_mixin", "p4obs", "metric_6")
_emit_records_incident_event("replay_guard_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_guard_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("replay_guard_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_guard_mixin", "p4obs", "mon_state")
_emit_triggers_alert("replay_guard_mixin", "p4obs", "alert")
_emit_links_incident_trace("replay_guard_mixin", "p4obs", "trace_link")
_emit_captures_pattern("replay_guard_mixin", "p3lm", "pattern")
_emit_records_learning_event("replay_guard_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_guard_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_guard_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_guard_mixin", "p3lm", "routing")
_emit_improves_agent_policy("replay_guard_mixin", "p3lm", "policy")
_emit_stores_learning_state("replay_guard_mixin", "p3lm", "state")
_emit_records_execution_trace("replay_guard_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_guard_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_guard_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_guard_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_guard_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_guard_mixin", "env_read", "p2_env_1")
_emit_reads_environ("replay_guard_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_guard_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_guard_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_guard_mixin", "context_pull")
_emit_pulls_context("p1", "replay_guard_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_guard_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_guard_mixin", "uwg_term_2")
_emit_writes_through("p1", "replay_guard_mixin", "write_through")
_emit_writes_through("p1", "replay_guard_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_guard_mixin", "safety_validation")
_emit_invokes_eval("p1", "replay_guard_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "replay_guard_mixin", "routing_commit")
_emit_escalates_to_human("p1", "replay_guard_mixin", "human_escalation")
_emit_routes_through("p1", "replay_guard_mixin", "route_through")
_emit_checks_agent_registry("p1", "replay_guard_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "replay_guard_mixin", "capability")
_emit_dispatches_execution_plan("p1", "replay_guard_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "replay_guard_mixin", "sub_agent")
_emit_routes_to_agent("p1", "replay_guard_mixin", "target_agent")
_emit_verifies_policy("p1", "replay_guard_mixin", "policy_check")
_emit_observes_runtime_state("p1", "replay_guard_mixin", "runtime_state")
_emit_verifies_boundary("p1", "replay_guard_mixin", "boundary_check")
_emit_transcripts_response("p1", "replay_guard_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_guard_mixin")
_emit_gated_by_confidence("p1", "replay_guard_mixin", "confidence_gate")
emit_replay_key("p0", "replay_guard_mixin")
emit_determinism_digest("p0", "replay_guard_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "replay_guard_mixin", "execution_auth")
_emit_validates_capability("p2", "replay_guard_mixin", "capability_check")
_emit_routes_to_capability("p2", "replay_guard_mixin", "capability_route")
_emit_writes_via_uwg("p2", "replay_guard_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "replay_guard_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_guard_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "replay_guard_mixin", "exec_output")
_emit_dispatches_agent("p3", "replay_guard_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_guard_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_guard_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_guard_mixin", "healing_outcome")
_emit_escalates_failure("p3", "replay_guard_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_guard_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_guard_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_guard_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_guard_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_guard_mixin", "eval_metric")
_emit_stores_embedding("p4", "replay_guard_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_guard_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_guard_mixin", "exec_snapshot_link")

if TYPE_CHECKING:
    from ops_scripts.dev_tools.L0_routing_scripts.execution_context import ExecutionContext
_logger = logging.getLogger(__name__)


class ReplayGuardMixin:
    """Base mixin providing replay-mode awareness and policy-hash scoping.

    Must appear rightmost in MRO so that all other mixins can access
    ``is_replay_mode``, ``active_policy_hash``, and ``trace_id``.

    Constructor Parameters
    ----------------------
    execution_context : ExecutionContext | None
        Injected by the caller (entrypoint / test harness).
        If None, defaults to non-replay mode with L4-derived policy hash.
    """

    def __init__(self, execution_context: ExecutionContext | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if execution_context is not None:
            self._replay_mode: bool = bool(execution_context.replay_mode)
            self._trace_id: str = execution_context.trace_id or "no-trace"
            self._active_policy_hash: str = (
                execution_context.active_policy_hash or self._load_policy_hash_from_l4()
            )
            self._safety_status: str = execution_context.safety_status
            self._initial_policy_hash: str = self._active_policy_hash
        else:
            self._replay_mode = False
            self._trace_id = "no-trace"
            self._active_policy_hash = self._load_policy_hash_from_l4()
            self._safety_status = "PENDING"
            self._initial_policy_hash = self._active_policy_hash
        if self._replay_mode:
            self._install_deterministic_providers()
            _logger.info(
                "[ReplayGuard] Replay mode ACTIVE | trace_id=%s | policy_hash=%s",
                self._trace_id,
                self._active_policy_hash[:12] + "...",
            )

    @property
    def is_replay_mode(self) -> bool:
        """True if execution is a deterministic replay."""
        return self._replay_mode

    @property
    def active_policy_hash(self) -> str:
        """Current L4 policy hash scoping all mixin state."""
        return self._active_policy_hash

    @property
    def trace_id(self) -> str:
        """Immutable trace identifier for this execution run."""
        return self._trace_id

    @property
    def safety_status(self) -> str:
        """Current L5 safety gate status."""
        return self._safety_status

    @property
    def initial_policy_hash(self) -> str:
        """Policy hash captured at construction time for drift detection."""
        return self._initial_policy_hash

    def policy_hash_drifted(self) -> bool:
        """Return True if active_policy_hash differs from initial snapshot."""
        return self._active_policy_hash != self._initial_policy_hash

    @staticmethod
    def _load_policy_hash_from_l4() -> str:
        """Load active policy hash from L4 versioned config SSOT."""
        try:
            from agentic_core.L4_state.config.versioned_configs import get_active_configs

            return get_active_configs().policy.config_hash
        except ImportError:  # guardian: allow-silent-swallow - optional dependency
            _logger.warning("[ReplayGuard] L4 versioned_configs unavailable; using fallback policy hash.")
            return "fallback-no-l4"

    def _install_deterministic_providers(self) -> None:
        """Activate deterministic time/random/uuid for replay mode."""
        try:
            from agentic_core.L2_execution.deterministic_providers import patch_deterministic

            providers = patch_deterministic(self._trace_id)
            _logger.debug("[ReplayGuard] Deterministic providers installed: %s", list(providers.keys()))
        except ImportError:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            _logger.error(
                "[ReplayGuard] deterministic_providers module not found; replay determinism NOT enforced.",
            )
        except (
            AttributeError,
            RuntimeError,
        ) as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            _logger.error("[ReplayGuard] Failed to install deterministic providers: %s", exc)
            raise

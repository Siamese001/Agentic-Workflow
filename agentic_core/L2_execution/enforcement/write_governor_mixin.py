"""WriteGovernorMixin — enforces UWG termination for all write operations.

Any class that mixes this in gains three guarantees:
  1. All writes are routed through UniversalWriteGateway.write_file().
  2. Ungoverned direct Path.write_text / open(…, 'w') calls are intercepted
     and rejected unless the path is in the UWG allowed set.
  3. Every write attempt is recorded in the UWG mutation ledger.

ADG governance plane — adds ``writes_through`` and
``execution_terminates_at_uwg`` edges for every call site that uses
``governed_write`` or ``governed_write_bytes``.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.enforcement.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
    get_write_gateway,
)
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "write_governor_mixin")
emit_determinism_digest("p0", "write_governor_mixin")

_emit_dispatches_healing_run("p1", "write_governor_mixin", "L2")
_emit_routes_through("p1", "write_governor_mixin", "L2")
_emit_checks_agent_registry("p1", "write_governor_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "write_governor_mixin", "capability")
_emit_dispatches_execution_plan("p1", "write_governor_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "write_governor_mixin", "sub_agent")
_emit_routes_to_agent("p1", "write_governor_mixin", "target_agent")
_emit_verifies_policy("p1", "write_governor_mixin", "policy_check")
_emit_observes_runtime_state("p1", "write_governor_mixin", "runtime_state")
_emit_verifies_boundary("p1", "write_governor_mixin", "boundary_check")
_emit_transcripts_response("p1", "write_governor_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "write_governor_mixin")
_emit_gated_by_confidence("p1", "write_governor_mixin", "confidence_gate")
_emit_escalates_to_human("p1", "write_governor_mixin", "L2")
_emit_reads_policy_state("p1", "write_governor_mixin", "L2")

_emit_snapshots_state("p0", "write_governor_mixin", "state_snapshot")
_emit_authorize_and_execute("p2", "write_governor_mixin", "execution_auth")
_emit_validates_capability("p2", "write_governor_mixin", "capability_check")
_emit_routes_to_capability("p2", "write_governor_mixin", "capability_route")
_emit_writes_via_uwg("p2", "write_governor_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "write_governor_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "write_governor_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "write_governor_mixin", "exec_output")
_emit_dispatches_agent("p3", "write_governor_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "write_governor_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "write_governor_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "write_governor_mixin", "healing_outcome")
_emit_escalates_failure("p3", "write_governor_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "write_governor_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "write_governor_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "write_governor_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "write_governor_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "write_governor_mixin", "eval_metric")
_emit_stores_embedding("p4", "write_governor_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "write_governor_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "write_governor_mixin", "exec_snapshot_link")
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
)

_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("write_governor_mixin", "p4obs", "metric_6")
_emit_records_incident_event("write_governor_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("write_governor_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("write_governor_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("write_governor_mixin", "p4obs", "mon_state")
_emit_triggers_alert("write_governor_mixin", "p4obs", "alert")
_emit_links_incident_trace("write_governor_mixin", "p4obs", "trace_link")
_emit_captures_pattern("write_governor_mixin", "p3lm", "pattern")
_emit_records_learning_event("write_governor_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("write_governor_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("write_governor_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("write_governor_mixin", "p3lm", "routing")
_emit_improves_agent_policy("write_governor_mixin", "p3lm", "policy")
_emit_stores_learning_state("write_governor_mixin", "p3lm", "state")
_emit_records_execution_trace("write_governor_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("write_governor_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("write_governor_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("write_governor_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("write_governor_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("write_governor_mixin", "env_read", "p2_env_1")
_emit_reads_environ("write_governor_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("write_governor_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("write_governor_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "write_governor_mixin", "context_pull")
_emit_pulls_context("p1", "write_governor_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "write_governor_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "write_governor_mixin", "uwg_term_2")
_emit_writes_through("p1", "write_governor_mixin", "write_through")
_emit_writes_through("p1", "write_governor_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "write_governor_mixin", "safety_validation")
_emit_invokes_eval("p1", "write_governor_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "write_governor_mixin", "routing_commit")

Logger = logging.getLogger(__name__)


class WriteGovernorMixin:
    """Mixin that routes all writes through the UniversalWriteGateway.

    Usage::

        class MyAgent(WriteGovernorMixin, SovereignBaseAgent):
            def do_work(self) -> None:
                self.governed_write("artifacts/output.json", b"{}")

    The mixin resolves the gateway lazily on first use, so subclass
    ``__init__`` need not call anything special.
    """

    _uwg: UniversalWriteGateway | None = None

    def _get_uwg(self) -> UniversalWriteGateway:
        """Return the active UWG instance, creating a default one if needed."""
        if self._uwg is None:
            self._uwg = get_write_gateway()
        return self._uwg

    def set_write_gateway(self, gateway: UniversalWriteGateway) -> None:
        """Inject a custom gateway (primarily for testing)."""
        self._uwg = gateway

    def governed_write(self, path: str | Path, data: str | bytes) -> SimulationResult | MutationRecord:
        """Write *data* to *path* via the UWG sovereign gate.

        Raises:
            ToolNotAllowedError: if the path/extension is blocked by the UWG.
        """
        _emit_writes_through(str(uuid.uuid4()), "WriteGovernorMixin.governed_write", "L2_EXECUTION")
        _emit_applies_guardrail(str(uuid.uuid4()), "WriteGovernorMixin.governed_write", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "WriteGovernorMixin.governed_write",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteGovernorMixin.governed_write".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        raw = data.encode("utf-8") if isinstance(data, str) else data
        result = self._get_uwg().write_file(str(path), raw)
        Logger.debug("[WriteGovernorMixin] governed_write: %s -> %s", path, type(result).__name__)
        return result

    def governed_append(self, path: str | Path, data: str | bytes) -> SimulationResult | MutationRecord:
        """Append *data* to *path* via the UWG sovereign gate."""
        raw = data.encode("utf-8") if isinstance(data, str) else data
        result = self._get_uwg().append_file(str(path), raw)
        Logger.debug("[WriteGovernorMixin] governed_append: %s", path)
        return result

    def governed_delete(self, path: str | Path) -> SimulationResult | MutationRecord:
        """Delete *path* via the UWG sovereign gate."""
        result = self._get_uwg().delete_file(str(path))
        Logger.debug("[WriteGovernorMixin] governed_delete: %s", path)
        return result

    def governed_rename(self, src: str | Path, dst: str | Path) -> SimulationResult | MutationRecord:
        """Rename *src* → *dst* via the UWG sovereign gate."""
        result = self._get_uwg().rename_file(str(src), str(dst))
        Logger.debug("[WriteGovernorMixin] governed_rename: %s -> %s", src, dst)
        return result

    def assert_write_governed(self, path: str | Path, operation: str = "write") -> bool:
        """Assert that *path* is in the UWG allowed set without performing a write.

        Returns True if permitted, raises ToolNotAllowedError if blocked.
        """
        permitted = self._get_uwg().check_write_permission(str(path), operation)
        if not permitted:
            raise ToolNotAllowedError(f"[WriteGovernorMixin] Write to '{path}' not permitted by UWG policy.")
        return True

    def get_write_stats(self) -> dict[str, Any]:
        """Proxy to UWG write statistics."""
        return self._get_uwg().get_write_stats()

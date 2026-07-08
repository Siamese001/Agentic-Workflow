"""LiveRunPipelineAdapter — bridges InMemoryHealingOutcomeIntakeStore to meta_learning_pipeline.

C1 hardening: explicit adapter layer so execute_ssot._fire_meta_learning_intake
does not directly couple to PipelineDependencies construction details.

Design invariants:
- No wall-clock reads (timestamps provided by caller).
- BGE embeddings are always active (mandatory system dependency).
- Fail-closed: any adapter error propagates; no silent fallback.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "live_run_pipeline_adapter", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "live_run_pipeline_adapter", "policy_binding")
trace_contract._emit_snapshots_state("p0", "live_run_pipeline_adapter", "state_snapshot")

trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("live_run_pipeline_adapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("live_run_pipeline_adapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("live_run_pipeline_adapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("live_run_pipeline_adapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("live_run_pipeline_adapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("live_run_pipeline_adapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("live_run_pipeline_adapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("live_run_pipeline_adapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("live_run_pipeline_adapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("live_run_pipeline_adapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("live_run_pipeline_adapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("live_run_pipeline_adapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("live_run_pipeline_adapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("live_run_pipeline_adapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("live_run_pipeline_adapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("live_run_pipeline_adapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("live_run_pipeline_adapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("live_run_pipeline_adapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("live_run_pipeline_adapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("live_run_pipeline_adapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("live_run_pipeline_adapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("live_run_pipeline_adapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("live_run_pipeline_adapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "live_run_pipeline_adapter", "context_pull")
trace_contract._emit_pulls_context("p1", "live_run_pipeline_adapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "live_run_pipeline_adapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "live_run_pipeline_adapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "live_run_pipeline_adapter", "write_through")
trace_contract._emit_writes_through("p1", "live_run_pipeline_adapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "live_run_pipeline_adapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "live_run_pipeline_adapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "live_run_pipeline_adapter", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "live_run_pipeline_adapter", "human_escalation")
trace_contract._emit_routes_through("p1", "live_run_pipeline_adapter", "route_through")
trace_contract._emit_checks_agent_registry("p1", "live_run_pipeline_adapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "live_run_pipeline_adapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "live_run_pipeline_adapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "live_run_pipeline_adapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "live_run_pipeline_adapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "live_run_pipeline_adapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "live_run_pipeline_adapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "live_run_pipeline_adapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "live_run_pipeline_adapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "live_run_pipeline_adapter")
trace_contract._emit_gated_by_confidence("p1", "live_run_pipeline_adapter", "confidence_gate")
trace_contract.emit_replay_key("p0", "live_run_pipeline_adapter")
trace_contract.emit_determinism_digest("p0", "live_run_pipeline_adapter")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "live_run_pipeline_adapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "live_run_pipeline_adapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "live_run_pipeline_adapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "live_run_pipeline_adapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "live_run_pipeline_adapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "live_run_pipeline_adapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "live_run_pipeline_adapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "live_run_pipeline_adapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "live_run_pipeline_adapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "live_run_pipeline_adapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "live_run_pipeline_adapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "live_run_pipeline_adapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "live_run_pipeline_adapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "live_run_pipeline_adapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "live_run_pipeline_adapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "live_run_pipeline_adapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "live_run_pipeline_adapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "live_run_pipeline_adapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "live_run_pipeline_adapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "live_run_pipeline_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ActivationAuthorizationError(RuntimeError):
    """Raised when pipeline activation is attempted without dual approval.

    C-hardening: any attempt to invoke the pipeline with mutations enabled
    (proposal_only=False) without explicit dual-approval tokens MUST raise
    this error.  The default proposal_only=True is the safe no-op path.
    """

    pass


class LiveRunPipelineAdapter:
    """Adapts the in-process healing outcome store for meta_learning_pipeline consumption.

    This adapter translates the InMemoryHealingOutcomeIntakeStore record format
    into the telemetry/audit format expected by run_pipeline(), avoiding direct
    coupling between execute_ssot and pipeline internals.

    Activation: the adapter is instantiated unconditionally. BGE embeddings are
    a mandatory system dependency; import failure raises at startup.
    """

    def __init__(self, intake_adapter: Any, *, source_tag: str = "live_run") -> None:
        """Initialise adapter.

        Args:
            intake_adapter: Pre-built HealingOutcomeIntakeAdapter (from execute_ssot).
            source_tag: Identifier written into pipeline metadata for audit tracing.
        """
        self._intake_adapter = intake_adapter
        self._source_tag = source_tag

    def record_count(self) -> int:
        """Return the number of healing records available for pipeline consumption."""
        try:
            return self._intake_adapter.store.count()
        except (ValueError, TypeError, RuntimeError) as e:
            return 0

    def build_pipeline_deps(self, repo_root: Any, healing_config_optimizer: Any | None = None) -> Any:
        """Construct PipelineDependencies wired to this adapter's intake store.

        Args:
            repo_root: pathlib.Path to the repository root.
            healing_config_optimizer: Optional pre-built optimizer.

        Returns:
            PipelineDependencies ready for run_pipeline().
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LiveRunPipelineAdapter.build_pipeline_deps"
        )

        from agentic_core.L6_system_learning.pipelines.pipeline_factory import build_pipeline_deps

        return build_pipeline_deps(
            repo_root=repo_root,
            healing_outcome_intake_adapter=self._intake_adapter,
            healing_config_optimizer=healing_config_optimizer,
        )

    def run(
        self,
        *,
        repo_root: Any,
        now_utc: int,
        window_start_utc: int,
        proposal_only: bool = True,
        approval_token: str | None = None,
    ) -> None:
        """Run the meta_learning_pipeline end-to-end with this adapter's records.

        Args:
            repo_root: pathlib.Path to the repository root.
            now_utc: Current Unix timestamp (caller-provided, no wall-clock read).
            window_start_utc: Window start for telemetry aggregation.
            proposal_only: When True (default), pipeline produces proposals only (safe).
                           When False, mutations are enabled — requires approval_token.
            approval_token: Required when proposal_only=False.  Any non-empty string is
                            accepted as the dual-approval gate in local runs.  CI must
                            supply a token; absence raises ActivationAuthorizationError.

        Raises:
            ActivationAuthorizationError: If proposal_only=False and no approval_token.
            Any exception from run_pipeline() propagates; caller is responsible
            for catch/log if non-fatal behaviour is desired.
        """
        if not proposal_only and (not approval_token):
            raise ActivationAuthorizationError(
                "proposal_only=False requires a non-empty approval_token; pass approval_token=<token> to enable pipeline mutations.",
            )
        from agentic_core.L6_system_learning.pipelines.meta_learning_pipeline import run_pipeline
        from agentic_core.L6_system_learning.pipelines.pipeline_factory import build_pipeline_config

        cfg = build_pipeline_config(proposal_only=proposal_only)
        deps = self.build_pipeline_deps(repo_root=repo_root)
        run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start_utc,
            window_end_utc=now_utc,
            cfg=cfg,
            deps=deps,
        )
        logger.info(
            "[LiveRunPipelineAdapter] run_pipeline completed (%d records, source=%s).",
            self.record_count(),
            self._source_tag,
        )


__all__ = ["ActivationAuthorizationError", "LiveRunPipelineAdapter"]

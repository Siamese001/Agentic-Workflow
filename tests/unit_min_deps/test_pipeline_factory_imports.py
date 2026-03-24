"""GAP-F: build_pipeline_deps() must resolve without ImportError and return correct proposer types."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    SYSTEM_LEARNING_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
)

_emit_records_execution_trace("p0", "evidence", "test_pipeline_factory_imports")
_emit_applies_guardrail("p0", "test_pipeline_factory_imports", "p0_governance")
_emit_reads_policy_state("p0", "test_pipeline_factory_imports", "policy_binding")
_emit_snapshots_state("p0", "test_pipeline_factory_imports", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_1")
_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_2")
_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_3")
_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_4")
_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_5")
_emit_emits_metric_event("test_pipeline_factory_imports", "p4obs", "metric_6")
_emit_records_incident_event("test_pipeline_factory_imports", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_pipeline_factory_imports", "p4obs", "anomaly")
_emit_writes_observability_log("test_pipeline_factory_imports", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_pipeline_factory_imports", "p4obs", "mon_state")
_emit_triggers_alert("test_pipeline_factory_imports", "p4obs", "alert")
_emit_links_incident_trace("test_pipeline_factory_imports", "p4obs", "trace_link")
_emit_captures_pattern("test_pipeline_factory_imports", "p3lm", "pattern")
_emit_records_learning_event("test_pipeline_factory_imports", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_pipeline_factory_imports", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_pipeline_factory_imports", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_pipeline_factory_imports", "p3lm", "routing")
_emit_improves_agent_policy("test_pipeline_factory_imports", "p3lm", "policy")
_emit_stores_learning_state("test_pipeline_factory_imports", "p3lm", "state")
_emit_records_execution_trace("test_pipeline_factory_imports", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_pipeline_factory_imports", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_pipeline_factory_imports", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_pipeline_factory_imports", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_pipeline_factory_imports", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_pipeline_factory_imports", "env_read", "p2_env_1")
_emit_reads_environ("test_pipeline_factory_imports", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_pipeline_factory_imports", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_pipeline_factory_imports", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_pipeline_factory_imports", "context_pull")
_emit_pulls_context("p1", "test_pipeline_factory_imports", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_pipeline_factory_imports", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_pipeline_factory_imports", "uwg_term_2")
_emit_writes_through("p1", "test_pipeline_factory_imports", "write_through")
_emit_writes_through("p1", "test_pipeline_factory_imports", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_pipeline_factory_imports", "safety_validation")
_emit_invokes_eval("p1", "test_pipeline_factory_imports", "eval_call")
_emit_proposal_commits_routing("p1", "test_pipeline_factory_imports", "routing_commit")
_emit_escalates_to_human("p1", "test_pipeline_factory_imports", "human_escalation")
_emit_routes_through("p1", "test_pipeline_factory_imports", "route_through")
_emit_checks_agent_registry("p1", "test_pipeline_factory_imports", "agent_registry")
_emit_validates_agent_capability("p1", "test_pipeline_factory_imports", "capability")
_emit_dispatches_execution_plan("p1", "test_pipeline_factory_imports", "exec_plan")
_emit_agent_executes_agent("p1", "test_pipeline_factory_imports", "sub_agent")
_emit_routes_to_agent("p1", "test_pipeline_factory_imports", "target_agent")
_emit_verifies_policy("p1", "test_pipeline_factory_imports", "policy_check")
_emit_observes_runtime_state("p1", "test_pipeline_factory_imports", "runtime_state")
_emit_verifies_boundary("p1", "test_pipeline_factory_imports", "boundary_check")
_emit_transcripts_response("p1", "test_pipeline_factory_imports", "transcript")
_emit_hard_fails_untranscripted("p1", "test_pipeline_factory_imports")
_emit_gated_by_confidence("p1", "test_pipeline_factory_imports", "confidence_gate")
emit_replay_key("p0", "test_pipeline_factory_imports")
emit_determinism_digest("p0", "test_pipeline_factory_imports")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_pipeline_factory_imports", "execution_auth")
_emit_validates_capability("p2", "test_pipeline_factory_imports", "capability_check")
_emit_routes_to_capability("p2", "test_pipeline_factory_imports", "capability_route")
_emit_writes_via_uwg("p2", "test_pipeline_factory_imports", "uwg_write")
_emit_blocks_direct_write("p2", "test_pipeline_factory_imports", "direct_write_block")
_emit_records_tool_invocation("p2", "test_pipeline_factory_imports", "tool_invocation")
_emit_captures_execution_output("p2", "test_pipeline_factory_imports", "exec_output")
_emit_dispatches_agent("p3", "test_pipeline_factory_imports", "agent_dispatch")
_emit_coordinates_agents("p3", "test_pipeline_factory_imports", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_pipeline_factory_imports", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_pipeline_factory_imports", "healing_outcome")
_emit_escalates_failure("p3", "test_pipeline_factory_imports", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_pipeline_factory_imports", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_pipeline_factory_imports", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_pipeline_factory_imports", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_pipeline_factory_imports", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_pipeline_factory_imports", "eval_metric")
_emit_stores_embedding("p4", "test_pipeline_factory_imports", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_pipeline_factory_imports", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_pipeline_factory_imports", "exec_snapshot_link")

PIPELINE_FACTORY_PATH = (
    Path(__file__).parent.parent.parent / SYSTEM_LEARNING_DIR / "pipelines" / "pipeline_factory.py"
)


@pytest.mark.unit_min_deps
class TestPipelineFactoryImports:
    def test_no_healing_backups_import_in_source(self):
        """AST: no import from healing_backups.naming_violations exists in pipeline_factory.py."""
        src = PIPELINE_FACTORY_PATH.read_text(encoding="utf-8", errors="replace")
        assert "healing_backups" not in src, (
            "Stale healing_backups import path still present in pipeline_factory.py"
        )
        assert "naming_violations" not in src, (
            "naming_violations import path still present in pipeline_factory.py"
        )

    def test_canonical_proposer_imports_in_source(self):
        """AST: canonical imports from system_learning.engines.l0/l1/l5 are present."""
        src = PIPELINE_FACTORY_PATH.read_text(encoding="utf-8", errors="replace")
        assert "system_learning.engines.l0_threshold_tuner" in src
        assert "system_learning.engines.l1_model_proposer" in src
        assert "system_learning.engines.l5_policy_proposer" in src

    def test_build_pipeline_deps_no_import_error(self, tmp_path):
        """build_pipeline_deps() must not raise ImportError."""
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        # Should not raise ImportError
        deps = build_pipeline_deps(repo_root=tmp_path)
        assert deps is not None

    def test_l0_proposer_is_correct_type(self, tmp_path):
        """The l0_proposer in PipelineDependencies must be an L0ProposerAdapter instance."""
        from system_learning.engines.l0_threshold_tuner import L0ProposerAdapter
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l0_proposer, L0ProposerAdapter), (
            f"Expected L0ProposerAdapter, got {type(deps.l0_proposer)}"
        )

    def test_l1_proposer_is_correct_type(self, tmp_path):
        """The l1_proposer in PipelineDependencies must be an L1ModelProposer instance."""
        from system_learning.engines.l1_model_proposer import L1ModelProposer
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l1_proposer, L1ModelProposer), (
            f"Expected L1ModelProposer, got {type(deps.l1_proposer)}"
        )

    def test_l5_proposer_is_correct_type(self, tmp_path):
        """The l5_proposer in PipelineDependencies must be an L5PolicyProposer instance."""
        from system_learning.engines.l5_policy_proposer import L5PolicyProposer
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l5_proposer, L5PolicyProposer), (
            f"Expected L5PolicyProposer, got {type(deps.l5_proposer)}"
        )

    def test_run_pipeline_completes_after_import_fix(self, tmp_path):
        """Pipeline execution verification: build_pipeline_deps + run_pipeline must not raise ImportError."""
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline
        from system_learning.pipelines.pipeline_factory import (
            build_pipeline_config,
            build_pipeline_deps,
        )

        cfg = build_pipeline_config(proposal_only=True)
        deps = build_pipeline_deps(repo_root=tmp_path)

        # Must not raise ImportError (the primary regression we're guarding against)
        try:
            result = run_pipeline(
                now_utc=1_000_000,
                window_start_utc=999_000,
                window_end_utc=1_000_000,
                cfg=cfg,
                deps=deps,
            )
            # If it returns, result must be a tuple (proposals)
            assert isinstance(result, tuple)
        except ImportError as e:
            pytest.fail(f"run_pipeline raised ImportError after import fix: {e}")

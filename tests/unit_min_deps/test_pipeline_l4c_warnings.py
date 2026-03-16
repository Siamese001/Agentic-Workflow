"""GAP-D: L4C write helpers must emit logger.warning on failure, never silent pass."""

import ast
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    SYSTEM_LEARNING_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_pipeline_l4c_warnings")
_emit_applies_guardrail("p0", "test_pipeline_l4c_warnings", "p0_governance")
_emit_snapshots_state("p0", "test_pipeline_l4c_warnings", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_1")
_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_2")
_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_3")
_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_4")
_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_5")
_emit_emits_metric_event("test_pipeline_l4c_warnings", "p4obs", "metric_6")
_emit_records_incident_event("test_pipeline_l4c_warnings", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_pipeline_l4c_warnings", "p4obs", "anomaly")
_emit_writes_observability_log("test_pipeline_l4c_warnings", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_pipeline_l4c_warnings", "p4obs", "mon_state")
_emit_triggers_alert("test_pipeline_l4c_warnings", "p4obs", "alert")
_emit_links_incident_trace("test_pipeline_l4c_warnings", "p4obs", "trace_link")
_emit_captures_pattern("test_pipeline_l4c_warnings", "p3lm", "pattern")
_emit_records_learning_event("test_pipeline_l4c_warnings", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_pipeline_l4c_warnings", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_pipeline_l4c_warnings", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_pipeline_l4c_warnings", "p3lm", "routing")
_emit_improves_agent_policy("test_pipeline_l4c_warnings", "p3lm", "policy")
_emit_stores_learning_state("test_pipeline_l4c_warnings", "p3lm", "state")
_emit_records_execution_trace("test_pipeline_l4c_warnings", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_pipeline_l4c_warnings", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_pipeline_l4c_warnings", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_pipeline_l4c_warnings", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_pipeline_l4c_warnings", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_pipeline_l4c_warnings", "env_read", "p2_env_1")
_emit_reads_environ("test_pipeline_l4c_warnings", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_pipeline_l4c_warnings", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_pipeline_l4c_warnings", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_pipeline_l4c_warnings", "context_pull")
_emit_pulls_context("p1", "test_pipeline_l4c_warnings", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_pipeline_l4c_warnings", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_pipeline_l4c_warnings", "uwg_term_2")
_emit_writes_through("p1", "test_pipeline_l4c_warnings", "write_through")
_emit_writes_through("p1", "test_pipeline_l4c_warnings", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_pipeline_l4c_warnings", "safety_validation")
_emit_invokes_eval("p1", "test_pipeline_l4c_warnings", "eval_call")
_emit_proposal_commits_routing("p1", "test_pipeline_l4c_warnings", "routing_commit")
emit_replay_key("p0", "test_pipeline_l4c_warnings")
emit_determinism_digest("p0", "test_pipeline_l4c_warnings")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_pipeline_l4c_warnings", "execution_auth")
_emit_validates_capability("p2", "test_pipeline_l4c_warnings", "capability_check")
_emit_routes_to_capability("p2", "test_pipeline_l4c_warnings", "capability_route")
_emit_writes_via_uwg("p2", "test_pipeline_l4c_warnings", "uwg_write")
_emit_blocks_direct_write("p2", "test_pipeline_l4c_warnings", "direct_write_block")
_emit_records_tool_invocation("p2", "test_pipeline_l4c_warnings", "tool_invocation")
_emit_captures_execution_output("p2", "test_pipeline_l4c_warnings", "exec_output")
_emit_dispatches_agent("p3", "test_pipeline_l4c_warnings", "agent_dispatch")
_emit_coordinates_agents("p3", "test_pipeline_l4c_warnings", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_pipeline_l4c_warnings", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_pipeline_l4c_warnings", "healing_outcome")
_emit_escalates_failure("p3", "test_pipeline_l4c_warnings", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_pipeline_l4c_warnings", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_pipeline_l4c_warnings", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_pipeline_l4c_warnings", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_pipeline_l4c_warnings", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_pipeline_l4c_warnings", "eval_metric")
_emit_stores_embedding("p4", "test_pipeline_l4c_warnings", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_pipeline_l4c_warnings", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_pipeline_l4c_warnings", "exec_snapshot_link")

META_PIPELINE_PATH = (
    Path(__file__).parent.parent.parent / SYSTEM_LEARNING_DIR / "pipelines" / "meta_learning_pipeline.py"
)


@pytest.mark.unit_min_deps
class TestPipelineL4cWarnings:
    def _count_silent_pass_in_l4_helpers(self):
        """AST: count bare 'except Exception: pass' blocks inside the three L4C helpers."""
        src = META_PIPELINE_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)

        helper_names = {
            "_analyze_shadow_drift_and_write",
            "_generate_policy_recommendation_and_write",
            "_create_proposal_and_write",
        }
        silent_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in helper_names:
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler):
                        # Check if the handler body is a single bare Pass
                        if len(child.body) == 1 and isinstance(child.body[0], ast.Pass):
                            silent_count += 1
        return silent_count

    def test_no_silent_pass_in_l4c_helpers_ast(self):
        """AST: zero bare 'except … pass' blocks remain in the three L4C helper functions."""
        count = self._count_silent_pass_in_l4_helpers()
        assert count == 0, f"{count} silent 'except ... pass' block(s) still present in L4C helpers"

    def test_shadow_drift_helper_warns_on_exception(self, caplog):
        """_analyze_shadow_drift_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _analyze_shadow_drift_and_write,
            _shadow_telemetry_batch,
        )

        # Inject a fake shadow record so the function doesn't short-circuit
        fake_record = MagicMock()
        _shadow_telemetry_batch.append(fake_record)

        mock_analyzer = MagicMock()
        drift_summary = MagicMock()
        drift_summary.to_canonical_json.return_value = "{}"
        mock_analyzer.analyze_batch.return_value = drift_summary

        mock_writer = MagicMock()
        mock_writer.write_l4c_shadow_drift.side_effect = RuntimeError("disk full")

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._shadow_drift_analyzer",
            mock_analyzer,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _analyze_shadow_drift_and_write(
                    profile_id="prof1", now_utc=1_000_000, l4_writer=mock_writer
                )

        _shadow_telemetry_batch.clear()

        assert result is drift_summary  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("shadow_drift" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C shadow_drift warning not emitted"
        )

    def test_policy_recommendation_helper_warns_on_exception(self, caplog):
        """_generate_policy_recommendation_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _generate_policy_recommendation_and_write,
        )

        mock_engine = MagicMock()
        recommendation = MagicMock()
        recommendation.to_canonical_json.return_value = "{}"
        mock_engine.generate_recommendation.return_value = recommendation

        mock_writer = MagicMock()
        mock_writer.write_l4c_policy_recommendation.side_effect = RuntimeError("write error")

        drift_summary = MagicMock()
        active_profile = MagicMock()

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._policy_recommendation_engine",
            mock_engine,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _generate_policy_recommendation_and_write(
                    drift_summary=drift_summary,
                    active_profile=active_profile,
                    now_utc=1_000_000,
                    l4_writer=mock_writer,
                )

        assert result is recommendation  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("policy_recommendation" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C policy_recommendation warning not emitted"
        )

    def test_create_proposal_helper_warns_on_exception(self, caplog):
        """_create_proposal_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        mock_manager = MagicMock()
        proposal = MagicMock()
        proposal.to_canonical_json.return_value = "{}"
        mock_manager.create_proposal.return_value = proposal

        mock_writer = MagicMock()
        mock_writer.write_l4c_retrieval_profile_proposal.side_effect = RuntimeError("no space")

        policy_rec = MagicMock()
        active_profile = MagicMock()

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._proposal_manager",
            mock_manager,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _create_proposal_and_write(
                    policy_recommendation=policy_rec,
                    active_profile=active_profile,
                    now_utc=1_000_000,
                    l4_writer=mock_writer,
                )

        assert result is proposal  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("proposal" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C retrieval_profile_proposal warning not emitted"
        )

    def test_pipeline_continues_after_l4c_failure(self, caplog):
        """L4C write failure must not propagate — pipeline returns normally."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        mock_manager = MagicMock()
        proposal = MagicMock()
        proposal.to_canonical_json.return_value = "{}"
        mock_manager.create_proposal.return_value = proposal

        # Writer raises on every call
        mock_writer = MagicMock()
        mock_writer.write_l4c_retrieval_profile_proposal.side_effect = OSError("io error")

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._proposal_manager",
            mock_manager,
        ):
            # Must not raise
            result = _create_proposal_and_write(
                policy_recommendation=MagicMock(),
                active_profile=MagicMock(),
                now_utc=1_000_000,
                l4_writer=mock_writer,
            )

        assert result is proposal

    def test_none_drift_summary_short_circuits_policy_helper(self):
        """Passing None drift_summary to _generate_policy_recommendation_and_write returns None."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _generate_policy_recommendation_and_write,
        )

        result = _generate_policy_recommendation_and_write(
            drift_summary=None,
            active_profile=MagicMock(),
            now_utc=1_000_000,
            l4_writer=MagicMock(),
        )
        assert result is None

    def test_none_policy_rec_short_circuits_proposal_helper(self):
        """Passing None policy_recommendation to _create_proposal_and_write returns None."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        result = _create_proposal_and_write(
            policy_recommendation=None,
            active_profile=MagicMock(),
            now_utc=1_000_000,
            l4_writer=MagicMock(),
        )
        assert result is None

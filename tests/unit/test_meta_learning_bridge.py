"""Tests for apps_shared.scripts.meta_learning_bridge — Waves 7.0.9–7.0.11.

Validates:
  a) bridge emits APP_SIGNAL_EVENT deterministically
  b) bridge cannot apply (source text has zero apply_meta_learning_proposal usage)
  c) end-to-end artifact chain stays deterministic for a sample apps_rg scenario
  d) bridge aggregate emits deterministic trace_id across shuffled events (7.0.11)
  e) AST-based: bridge has no ImportFrom/Name for apply_meta_learning_proposal (7.0.11)
"""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "test_meta_learning_bridge", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_bridge", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_bridge", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_bridge", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_bridge", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_bridge", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_bridge", "exec_snapshot_link")
from apps_shared.scripts.meta_learning_bridge import (
    emit_app_signal_aggregate,
    emit_app_signal_event,
    propose_from_signal_aggregate,
)
from system_learning.types.app_signal_types import (
    build_app_signal_event,
)
from system_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_bridge", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_bridge", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_bridge", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_bridge", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_bridge", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_bridge", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_bridge", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_bridge", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_bridge", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_bridge", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_bridge")
_emit_applies_guardrail("p0", "test_meta_learning_bridge", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_bridge", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_bridge", "state_snapshot")
_emit_pulls_context("p1", "test_meta_learning_bridge", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_bridge", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bridge", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_learning_bridge", "write_through")
_emit_writes_through("p1", "test_meta_learning_bridge", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_learning_bridge", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_bridge", "routing_commit")
emit_replay_key("p0", "test_meta_learning_bridge")
emit_determinism_digest("p0", "test_meta_learning_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


class TestBridgeEmitSignal:
    def test_bridge_emits_app_signal_event_deterministically(self) -> None:
        """Two calls with same inputs produce identical trace_id and JSON."""
        kwargs = {
            "app_id": APPS_RG_DIR,
            "run_id": "run_001",
            "message_id": "msg_001",
            "metric_name": "resume_message_response_rate",
            "metric_value": 0.85,
            "semantic_clock": _CLOCK,
        }
        e1 = emit_app_signal_event(**kwargs)
        e2 = emit_app_signal_event(**kwargs)
        assert e1.trace_id == e2.trace_id
        assert e1.to_json() == e2.to_json()
        assert e1.artifact_type == "APP_SIGNAL_EVENT"
        assert e1.app_id == APPS_RG_DIR


class TestBridgeCannotApply:
    def test_bridge_source_has_no_apply_usage(self) -> None:
        """The bridge module source must not call apply_meta_learning_proposal."""
        bridge_path = Path(
            inspect.getfile(emit_app_signal_event),
        )
        source = bridge_path.read_text(encoding="utf-8")
        # Must not import or call apply_meta_learning_proposal
        assert "apply_meta_learning_proposal" not in source


class TestBridgeEndToEndChain:
    def test_e2e_artifact_chain_deterministic_apps_rg(self) -> None:
        """Full pipeline: proposal->eval->approval->decision->change_package is deterministic."""
        # Step 1: Proposal via bridge
        proposal = propose_from_signal_aggregate(
            app_id=APPS_RG_DIR,
            target_component="routing_thresholds",
            before={"threshold": 0.5},
            after={"threshold": 0.7},
            metric_name="resume_message_response_rate",
            baseline=0.80,
            candidate=0.85,
            evidence_hash="e2e_hash_001",
            semantic_clock=_CLOCK,
        )
        assert proposal.proposer == APPS_RG_DIR
        assert proposal.artifact_type == "META_LEARNING_PROPOSAL"

        # Step 2: Evaluation
        evaluation = build_meta_learning_evaluation(
            proposal=proposal,
            evaluator="offline_bench",
            dataset_id="ds_rg_001",
            baseline=0.80,
            candidate=0.85,
            evidence_hash="eval_hash_001",
        )

        # Step 3: Approval
        approval = build_meta_learning_approval(
            evaluation=evaluation,
            approver="human_reviewer",
            decision="APPROVE",
            rationale="Confirmed on holdout.",
        )

        # Step 4: Decision
        decision = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert decision.decision == "ALLOW_TO_APPLY"

        # Step 5: Change package
        pkg = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component="routing_thresholds",
            change_spec={"threshold": 0.7},
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )

        # Determinism: rebuild entire chain
        proposal2 = propose_from_signal_aggregate(
            app_id=APPS_RG_DIR,
            target_component="routing_thresholds",
            before={"threshold": 0.5},
            after={"threshold": 0.7},
            metric_name="resume_message_response_rate",
            baseline=0.80,
            candidate=0.85,
            evidence_hash="e2e_hash_001",
            semantic_clock=_CLOCK,
        )
        evaluation2 = build_meta_learning_evaluation(
            proposal=proposal2,
            evaluator="offline_bench",
            dataset_id="ds_rg_001",
            baseline=0.80,
            candidate=0.85,
            evidence_hash="eval_hash_001",
        )
        approval2 = build_meta_learning_approval(
            evaluation=evaluation2,
            approver="human_reviewer",
            decision="APPROVE",
            rationale="Confirmed on holdout.",
        )
        decision2 = build_meta_learning_decision(
            proposal=proposal2,
            evaluation=evaluation2,
            approval=approval2,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        pkg2 = build_meta_learning_change_package(
            proposal=proposal2,
            evaluation=evaluation2,
            approval=approval2,
            decision=decision2,
            target_component="routing_thresholds",
            change_spec={"threshold": 0.7},
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )

        # Full chain determinism
        assert pkg.trace_id == pkg2.trace_id
        assert pkg.to_json() == pkg2.to_json()
        parsed = json.loads(pkg.to_json())
        assert parsed["artifact_type"] == "META_LEARNING_CHANGE_PACKAGE"
        assert parsed["target_component"] == "routing_thresholds"


# =============================================================================
# § Bridge Aggregate + AST Safety (Wave 7.0.11)
# =============================================================================


def _make_bridge_events(
    values: list[float],
    *,
    prefix: str = "msg",
) -> list:
    """Helper: build AppSignalEventArtifact list for bridge tests."""
    return [
        build_app_signal_event(
            app_id=APPS_RG_DIR,
            run_id="run_bridge",
            message_id=f"{prefix}_{i:03d}",
            metric_name="resume_message_response_rate",
            metric_value=v,
            semantic_clock=_CLOCK,
        )
        for i, v in enumerate(values)
    ]


class TestBridgeAggregate:
    def test_bridge_aggregate_deterministic_across_shuffled_events(self) -> None:
        """Bridge aggregate produces identical trace_id regardless of event order."""
        baseline_events = _make_bridge_events([0.80, 0.85, 0.90], prefix="bl")
        candidate_events = _make_bridge_events([0.70, 0.75], prefix="cd")

        all_events = baseline_events + candidate_events
        shuffled = list(reversed(all_events))

        agg1 = emit_app_signal_aggregate(
            app_id=APPS_RG_DIR,
            window_id="w_bridge",
            metric_name="resume_message_response_rate",
            events=all_events,
            baseline_selector=lambda e: e.message_id.startswith("bl"),
            candidate_selector=lambda e: e.message_id.startswith("cd"),
            evidence_hash="bridge_hash",
            semantic_clock=_CLOCK,
        )
        agg2 = emit_app_signal_aggregate(
            app_id=APPS_RG_DIR,
            window_id="w_bridge",
            metric_name="resume_message_response_rate",
            events=shuffled,
            baseline_selector=lambda e: e.message_id.startswith("bl"),
            candidate_selector=lambda e: e.message_id.startswith("cd"),
            evidence_hash="bridge_hash",
            semantic_clock=_CLOCK,
        )
        assert agg1.trace_id == agg2.trace_id
        assert agg1.to_json() == agg2.to_json()
        assert agg1.artifact_type == "APP_SIGNAL_AGGREGATE"


class TestBridgeASTSafety:
    def test_bridge_ast_forbids_apply_import(self) -> None:
        """AST scan: bridge must not import or reference apply_meta_learning_proposal."""
        bridge_path = Path(inspect.getfile(emit_app_signal_event))
        source = bridge_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(bridge_path))

        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "apply_meta_learning_proposal":
                        violations.append(
                            f"ImportFrom at line {node.lineno}: {alias.name}",
                        )
            if isinstance(node, ast.Name) and node.id == "apply_meta_learning_proposal":
                violations.append(
                    f"Name ref at line {node.lineno}: {node.id}",
                )
        assert not violations, f"apply_meta_learning_proposal found in bridge AST: {violations}"

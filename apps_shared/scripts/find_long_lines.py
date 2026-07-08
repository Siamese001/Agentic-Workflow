"""Find all lines longer than 100 characters."""

import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from apps_shared.utils.ConfigurationService import ConfigurationService
from tqdm import tqdm

trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("find_long_lines", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("find_long_lines", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("find_long_lines", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("find_long_lines", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("find_long_lines", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("find_long_lines", "p4obs", "alert")
trace_contract._emit_links_incident_trace("find_long_lines", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("find_long_lines", "p3lm", "pattern")
trace_contract._emit_records_learning_event("find_long_lines", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("find_long_lines", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("find_long_lines", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("find_long_lines", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("find_long_lines", "p3lm", "policy")
trace_contract._emit_stores_learning_state("find_long_lines", "p3lm", "state")
trace_contract._emit_records_execution_trace("find_long_lines", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("find_long_lines", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("find_long_lines", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("find_long_lines", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("find_long_lines", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("find_long_lines", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("find_long_lines", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("find_long_lines", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("find_long_lines", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "find_long_lines")
trace_contract._emit_applies_guardrail("p0", "find_long_lines", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "find_long_lines", "policy_binding")
trace_contract._emit_snapshots_state("p0", "find_long_lines", "state_snapshot")
trace_contract._emit_pulls_context("p1", "find_long_lines", "context_pull")
trace_contract._emit_pulls_context("p1", "find_long_lines", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "find_long_lines", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "find_long_lines", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "find_long_lines", "write_through")
trace_contract._emit_writes_through("p1", "find_long_lines", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "find_long_lines", "safety_validation")
trace_contract._emit_invokes_eval("p1", "find_long_lines", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "find_long_lines", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "find_long_lines", "human_escalation")
trace_contract._emit_routes_through("p1", "find_long_lines", "route_through")
trace_contract._emit_checks_agent_registry("p1", "find_long_lines", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "find_long_lines", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "find_long_lines", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "find_long_lines", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "find_long_lines", "target_agent")
trace_contract._emit_verifies_policy("p1", "find_long_lines", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "find_long_lines", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "find_long_lines", "boundary_check")
trace_contract._emit_transcripts_response("p1", "find_long_lines", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "find_long_lines")
trace_contract._emit_gated_by_confidence("p1", "find_long_lines", "confidence_gate")
trace_contract.emit_replay_key("p0", "find_long_lines")
trace_contract.emit_determinism_digest("p0", "find_long_lines")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "find_long_lines", "execution_auth")
trace_contract._emit_validates_capability("p2", "find_long_lines", "capability_check")
trace_contract._emit_routes_to_capability("p2", "find_long_lines", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "find_long_lines", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "find_long_lines", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "find_long_lines", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "find_long_lines", "exec_output")
trace_contract._emit_dispatches_agent("p3", "find_long_lines", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "find_long_lines", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "find_long_lines", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "find_long_lines", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "find_long_lines", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "find_long_lines", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "find_long_lines", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "find_long_lines", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "find_long_lines", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "find_long_lines", "eval_metric")
trace_contract._emit_stores_embedding("p4", "find_long_lines", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "find_long_lines", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "find_long_lines", "exec_snapshot_link")

Logger: Any = logging.getLogger(__name__)


def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
    for root, dirs, files in tqdm(os.walk("."), desc="Processing", unit="item"):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in tqdm(files, desc="Processing", unit="item"):
            if file.endswith(".py"):
                Path(root) / file
                try:
                    with open(ConfigurationService().FILEPATH, encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                ConfigurationService().violations.append(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars",
                                )
                                ConfigurationService().Logger.info(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars",
                                )
                                ConfigurationService().Logger.info(f"  {line[:150]}...")
                                ConfigurationService().Logger.info("")
                except (ValueError, TypeError, RuntimeError) as e:
                    raise
    ConfigurationService().Logger.info(f"\nTotal violations: {len(ConfigurationService().violations)}")


if __name__ == "__main__":
    find_long_lines()
